import os
import sys
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inference import EdgeInference
from src.model.train import VIRUS_DB
import random

def generate_batch(signature, count, mutation_rate=0.02):
    """Genera un lote de secuencias con mutaciones leves sobre una firma base."""
    batch = []
    bases = ['A','C','G','T']
    sig_len = len(signature)
    
    for _ in range(count):
        # Mutar
        seq_list = list(signature)
        num_mutations = int(sig_len * mutation_rate)
        for _ in range(num_mutations):
            idx = random.randint(0, sig_len-1)
            seq_list[idx] = random.choice(bases)
        
        # Tomar un fragmento aleatorio de 100bp (o rellenar)
        if sig_len > 100:
            start = random.randint(0, sig_len - 100)
            final_seq = "".join(seq_list[start:start+100])
        else:
            final_seq = "".join(seq_list).ljust(100, 'N') # Padding simple
            
        batch.append(final_seq)
    return batch

def evaluate_model(virus_name, model_path, target_signature, decoy_signature=None):
    print(f"\n{'='*60}")
    print(f"📊 REPORT DE VALIDACIÓN: {virus_name.upper()}")
    print(f"{'='*60}")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Modelo no encontrado en {model_path}")
        return

    # 1. Cargar Motor
    try:
        engine = EdgeInference(model_path=model_path)
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return

    # 2. Generar Dataset de Prueba (Test Set) - Fresco, no usado en training
    # Generamos 300 muestras: 100 Target, 100 Decoy (Otro Virus), 100 Ruido
    print(f"🧪 Generando set de prueba sintético (N=300)...")
    
    # Target (Class 1)
    # X_pos, y_pos = generate_synthetic_data(target_signature, num_samples=100, mutation_rate=0.02)
    sample_seqs = generate_batch(target_signature, 100)
    y_pos = np.ones(100) 
    
    # Decoy (Class 0 - Hard Negative)
    if decoy_signature:
        decoy_seqs = generate_batch(decoy_signature, 100)
    else:
        decoy_seqs = ["A"*100] * 100
    y_decoy = np.zeros(100)

    # Noise (Class 0 - Easy Negative)
    X_noise = []
    bases = ['A','C','G','T']
    for _ in range(100):
        X_noise.append("".join([random.choice(bases) for _ in range(100)]))
    y_noise = np.zeros(100)

    # Combinar
    X_test = sample_seqs + decoy_seqs + X_noise
    y_true = np.concatenate([y_pos, y_decoy, y_noise])
    
    # 3. Inferencia Masiva
    print(f"⚡ Ejecutando inferencia...")
    y_pred = []
    latencies = []
    
    for seq in X_test:
        label_text, conf, lat = engine.predict(seq)
        latencies.append(lat)
        # Convertir texto a clase (1 o 0)
        # inference.py returns "Viral" (1) or "Clean" (0)
        if "Viral" in label_text:
            y_pred.append(1)
        else:
            y_pred.append(0)
            
    y_pred = np.array(y_pred)

    # 4. Cálculo de KPIs
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    sensitivity = tp / (tp + fn) if (tp+fn) > 0 else 0 # Recall
    specificity = tn / (tn + fp) if (tn+fp) > 0 else 0 
    accuracy = accuracy_score(y_true, y_pred)
    avg_latency = np.mean(latencies)

    # 5. Imprimir Reporte
    print(f"\n📈 RENDIMIENTO (KPIs):")
    print(f"   Accuracy Global:   {accuracy*100:.2f}%  (Objetivo: >95%)")
    print(f"   Sensibilidad (TP): {sensitivity*100:.2f}%  (Detectar el virus correctamente)")
    print(f"   Especificidad (TN):{specificity*100:.2f}%  (Rechazar otros virus/ruido)")
    print(f"   Latencia Promedio: {avg_latency:.2f} ms")

    print(f"\n🔍 MATRIZ DE CONFUSIÓN DETALLADA:")
    print(f"   [Verdadero Positivo]: {tp}  (Detectados OK)")
    print(f"   [Falso Negativo]:     {fn}  (Virus perdidos)")
    print(f"   [Verdadero Negativo]: {tn}  (Sanos/Otros rechazados OK)")
    print(f"   [Falso Positivo]:     {fp}  (ALERTAS FALSAS - CRÍTICO)")

    # Análisis de fallos específicos (Decoy vs Ruido)
    # Los primeros 100 son Target, siguientes 100 Decoy, ultimos 100 Ruido
    fp_decoy = np.sum(y_pred[100:200])
    fp_noise = np.sum(y_pred[200:300])
    
    if fp > 0:
        print(f"\n🕵️ ANÁLISIS DE FALSOS POSITIVOS:")
        print(f"   Confundió el OTRO VIRUS con este: {fp_decoy} veces")
        print(f"   Confundió RUIDO con este:         {fp_noise} veces")
    
    # Veredicto
    limit_acc = 0.95
    limit_spec = 0.90
    
    if accuracy >= limit_acc and specificity >= limit_spec:
        print(f"\n✅ ESTADO: APROBADO (Listo para Demo)")
    else:
        print(f"\n⚠️ ESTADO: REQUIERE MEJORA (Re-entrenar)")

def main():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_path = os.path.join(base_path, 'data')
    model_dir = os.path.join(data_path, 'models')
    
    # Cargar genomas para test desde la DB compartida
    covid_sig = VIRUS_DB['covid19']['signature']
    h3n2_sig = VIRUS_DB['h3n2']['signature']
    
    # Evaluar COVID (Target=Covid, Decoy=H3N2)
    # Target label en display, model path, target sig, decoy sig
    evaluate_model("SARS-CoV-2", os.path.join(model_dir, 'model_covid.tflite'), covid_sig, h3n2_sig)

    # Evaluar H3N2 (Target=H3N2, Decoy=Covid)
    evaluate_model("Influenza H3N2", os.path.join(model_dir, 'model_h3n2.tflite'), h3n2_sig, covid_sig)

if __name__ == "__main__":
    main()
