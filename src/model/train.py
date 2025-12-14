import numpy as np
import tensorflow as tf
import os
import sys
import argparse

# Add src to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.preprocessing.encoder import DNAEncoder
from src.model.cnn import create_genomic_cnn

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models')

# Genetic Signatures (Simplified for Demo)
VIRUS_DB = {
    'covid19': {
        'name': 'SARS-CoV-2',
        # Spike protein fragment
        'signature': "ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACAC",
        'filename': 'model_covid.tflite'
    },
    'h3n2': {
        'name': 'Influenza A (H3N2)',
        # Hemagglutinin (HA) gene fragment example
        'signature': "ATGAAGACCATCATTGCTTTGAGCTACATTTTCTGTCTGGCTCTCGGCCAAGACCTTCCAGGAAATGACAACAGCACAGCAACGCTGTGCCTGGGACACC",
        'filename': 'model_h3n2.tflite'
    }
}

def generate_synthetic_data(target_virus, num_samples=2000):
    """
    Genera datos sintéticos.
    Clase 1 (Positivo): Virus Objetivo.
    Clase 0 (Negativo): Ruido Aleatorio + OTROS Virus (para evitar falsos positivos).
    """
    encoder = DNAEncoder(method='integer', max_length=100)
    X = []
    y = []
    
    viral_data = VIRUS_DB.get(target_virus)
    if not viral_data:
        raise ValueError(f"Unknown target: {target_virus}")
    
    # Identify Decoys (viruses that are NOT the target)
    decoys = [v['signature'] for k, v in VIRUS_DB.items() if k != target_virus]
        
    viral_signature = viral_data['signature']
    print(f"[Train] Generando {num_samples} muestras para {viral_data['name']} (con contra-ejemplos)...")
    
    for i in range(num_samples):
        # 50% Positives, 50% Negatives
        is_target = i % 2 == 0
        
        if is_target:
            # TARGET VIRUS (Positivo)
            start = (i * 3) % len(viral_signature)
            seq = viral_signature[start:start+100]
            if len(seq) < 100: seq = seq.ljust(100, 'A')
            label = 1
        else:
            # NEGATIVE CLASS (Ruido o Decoy)
            # Aumentamos Hard Negatives: 50% de los negativos serán Decoys (Otro Virus)
            # Indices negativos son impares: 1, 3, 5...
            # Queremos que la mitad de esos sean decoys.
            
            use_decoy = (i % 4) == 1 # Antes era así (25% del total, 50% de negativos)
            # Vamos a ser más agresivos: Si hay decoys, usarlo casi siempre que no sea target
            # para purgar falsos positivos.
            
            if decoys:
                 # Alternar entre decoy y ruido puro
                 use_decoy = (i % 4) in [1, 3] # Esto haría que TODOS los negativos sean decoy? No.
                 # i: 0(T), 1(N), 2(T), 3(N)...
                 # Si quiero solidez, mezclemos.
                 
                 import random
                 if random.random() < 0.7:  # 70% de los negativos serán el OTRO virus
                    decoy_sig = decoys[0] 
                    start = (i * 7) % len(decoy_sig) # Offset distinto
                    seq = decoy_sig[start:start+100]
                    if len(seq) < 100: seq = seq.ljust(100, 'C')
                 else:
                    # 30% Ruido random
                    bases = ['A', 'C', 'G', 'T']
                    seq = "".join([random.choice(bases) for _ in range(100)])
            else:
                # Solo ruido si no hay decoys
                bases = ['A', 'C', 'G', 'T']
                seq = "".join([random.choice(bases) for _ in range(100)])
            
            label = 0
            
        X.append(encoder.encode(seq))
        y.append(label)
        
    return np.array(X), np.array(y)

def train_and_convert(target_virus):
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 1. Get Data
    X_train, y_train = generate_synthetic_data(target_virus, 2000)
    
    # 2. Create Model
    model = create_genomic_cnn(input_length=100, num_classes=2)
    
    # 3. Train
    print("[Train] Iniciando entrenamiento de la CNN...")
    # Quick training
    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2, verbose=1)
    
    # 4. Save Keras Model (Temporary)
    keras_path = os.path.join(MODEL_DIR, f'temp_{target_virus}.h5')
    model.save(keras_path)
    
    # 5. Convert to TFLite (Quantization)
    print(f"[TFLite] Convirtiendo modelo {target_virus}...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    def representative_dataset():
        for i in range(100):
            yield [X_train[i].astype(np.float32).reshape(1, 100)]

    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()
    
    final_filename = VIRUS_DB[target_virus]['filename']
    tflite_path = os.path.join(MODEL_DIR, final_filename)
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
        
    print(f"[Success] Modelo {final_filename} guardado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, default='all', choices=['covid19', 'h3n2', 'all'])
    args = parser.parse_args()
    
    if args.target == 'all':
        for v in ['covid19', 'h3n2']:
            train_and_convert(v)
    else:
        train_and_convert(args.target)
