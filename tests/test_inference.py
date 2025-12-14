import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar condicionalmente para evitar errores si TF no está instalado en CI
try:
    from src.inference import EdgeInference
except ImportError:
    EdgeInference = None

class TestInferenceEngine(unittest.TestCase):
    def setUp(self):
        if EdgeInference is None:
            self.skipTest("TensorFlow no instalado")

    @patch('src.inference.tf.lite.Interpreter')
    def test_predict_call(self, mock_interpreter_cls):
        """
        Prueba que el método predict invoque al intérprete correctamente.
        No probamos el modelo real TFLite aquí, sino la lógica del wrapper.
        """
        # Mock del TFLite Interpreter
        mock_interpreter = MagicMock()
        mock_interpreter_cls.return_value = mock_interpreter
        
        # Configurar mocks de input/output details
        mock_interpreter.get_input_details.return_value = [{'index': 0}]
        # Mock output: scale=1.0, zero_point=0 for simplicity
        mock_interpreter.get_output_details.return_value = [{'index': 1, 'quantization': (1.0, 0)}]
        
        # Mock result tensor: [0.1, 0.9] -> Clase 1 (Virus) con alta confianza
        mock_interpreter.get_tensor.return_value = np.array([[0.1, 0.9]], dtype=np.float32)

        # Instanciar (bypass file checking)
        with patch('os.path.exists', return_value=True):
            engine = EdgeInference(model_path="dummy.tflite")
        
        pathogen, confidence, latency = engine.predict("ACGT")
        
        # Verificaciones
        mock_interpreter.allocate_tensors.assert_called_once()
        mock_interpreter.invoke.assert_called_once()
        
        self.assertIn("Viral", pathogen)
        self.assertAlmostEqual(confidence, 0.9)
        self.assertIsInstance(latency, float)

if __name__ == '__main__':
    unittest.main()
