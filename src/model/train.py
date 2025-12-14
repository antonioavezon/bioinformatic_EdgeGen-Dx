import numpy as np
import tensorflow as tf
import os
import sys

# Add src to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.preprocessing.encoder import DNAEncoder
from src.model.cnn import create_genomic_cnn

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models')

def generate_synthetic_data(num_samples=1000):
    """Genera datos sintéticos para entrenamiento rápido de la demo."""
    encoder = DNAEncoder(method='integer', max_length=100)
    X = []
    y = []
    
    # Virus signature (same as ingestion)
    viral_signature = "ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACAC"
    
    print(f"[Train] Generando {num_samples} muestras sintéticas...")
    for i in range(num_samples):
        is_viral = i % 2 == 0
        if is_viral:
            # Viral sequence with some mutation/noise
            start = (i * 3) % len(viral_signature)
            seq = viral_signature[start:start+100]
            if len(seq) < 100: seq = seq.ljust(100, 'A')
            label = 1
        else:
            # Random DNA
            import random
            bases = ['A', 'C', 'G', 'T']
            seq = "".join([random.choice(bases) for _ in range(100)])
            label = 0
            
        X.append(encoder.encode(seq))
        y.append(label)
        
    return np.array(X), np.array(y)

def train_and_convert():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 1. Get Data
    X_train, y_train = generate_synthetic_data(2000)
    
    # 2. Create Model
    model = create_genomic_cnn(input_length=100, num_classes=2)
    
    # 3. Train
    print("[Train] Iniciando entrenamiento de la CNN...")
    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2)
    
    # 4. Save Keras Model
    keras_path = os.path.join(MODEL_DIR, 'edgegen_model.h5')
    model.save(keras_path)
    print(f"[Save] Modelo Keras guardado en: {keras_path}")
    
    # 5. Convert to TFLite (Quantization)
    print("[TFLite] Convirtiendo a formato optimizado (Int8)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Representative dataset for quantization
    def representative_dataset():
        for i in range(100):
            yield [X_train[i].astype(np.float32).reshape(1, 100)]

    converter.representative_dataset = representative_dataset
    # Ensure full integer quantization for Edge TPU compatibility (optional but good for 'Edge' theme)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()
    
    tflite_path = os.path.join(MODEL_DIR, 'edgegen_quant.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
        
    print(f"[Save] Modelo TFLite cuantizado guardado en: {tflite_path}")
    print(f"[Info] Tamaño original: {os.path.getsize(keras_path)/1024:.2f} KB")
    print(f"[Info] Tamaño TFLite: {os.path.getsize(tflite_path)/1024:.2f} KB")

if __name__ == "__main__":
    train_and_convert()
