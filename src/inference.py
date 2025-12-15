import numpy as np
import tensorflow as tf
import time
import os
import sys

# Agregar path para importar módulos locales si es necesario
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.preprocessing.encoder import DNAEncoder

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models', 'edgegen_quant.tflite')

class EdgeInference:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado en: {self.model_path}. Entrena primero!")
            
        # Cargar TFLite Model
        self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.encoder = DNAEncoder(method='integer', max_length=100)

    def predict(self, sequence):
        """
        Realiza la inferencia sobre una secuencia de ADN.
        Retorna: (clase_predicha, confianza, tiempo_ms)
        """
        # 1. Preproceso
        input_data = self.encoder.encode(sequence)
        
        # Check model input type (INT8 vs FLOAT32)
        input_dtype = self.input_details[0]['dtype']
        
        if input_dtype == np.float32:
            input_tensor = np.expand_dims(input_data, axis=0).astype(np.float32)
        else:
            input_tensor = np.expand_dims(input_data, axis=0).astype(np.int8)

        # 2. Set tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)

        # 3. Invocar intérprete (Inferencia)
        start_time = time.time()
        self.interpreter.invoke()
        end_time = time.time()
        
        # 4. Leer salida
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Dequantization si es necesario
        scale, zero_point = self.output_details[0]['quantization']
        
        if scale > 0:
            # Quantized model (int8 output)
            output_probs = (output_data.astype(np.float32) - zero_point) * scale
        else:
            # Float model directly
            output_probs = output_data[0] # output_data shape (1, 2)
            
        predicted_class = np.argmax(output_probs)
        # Handle shape differences for confidence
        if output_probs.ndim == 1: 
             confidence = output_probs[predicted_class]
        else:
             confidence = output_probs[0][predicted_class]
        
        # Normalizar confianza a 0-100% (esto es un estimado para la demo)
        # En int8 signed, va de -128 a 127.
        if scale > 0:
             # Just displaying the raw value converted directly isn't elegant manually
             # Let's rely on argmax mostly.
             pass
             
        # Para la demo, "Virus Objetivo" es clase 1
        pathogen = "Viral" if predicted_class == 1 else "Clean"
        
        latency_ms = (end_time - start_time) * 1000
        return pathogen, confidence, latency_ms

if __name__ == "__main__":
    # Test
    classifier = EdgeInference()
    seq_viral = "ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACAC"
    pat, conf, lat = classifier.predict(seq_viral)
    print(f"Predicción Test: {pat} | Latencia: {lat:.2f}ms")
