import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ingestion import download_reference_genome, SARS_COV_2_REF_URL

class TestDataIngestion(unittest.TestCase):
    
    @patch('src.ingestion.urllib.request.urlretrieve')
    def test_download_reference_genome_calls_correct_url(self, mock_urlretrieve):
        """
        Verifica que la función intente descargar desde la URL correcta de NCBI.
        No realiza la descarga real para no consumir ancho de banda en CI/Test.
        """
        # Ejecutar función
        with patch('os.path.exists', return_value=False): # Forzar intento de descarga
            download_reference_genome()
            
        # Verificar llamada
        args, _ = mock_urlretrieve.call_args
        download_url = args[0]
        
        self.assertEqual(download_url, SARS_COV_2_REF_URL)
        print(f"\n[Test] Verificado intento de descarga desde: {download_url}")

    def test_covid_reference_url_validity(self):
        """
        Verifica que la URL de referencia sea de un dominio confiable (NCBI).
        """
        self.assertIn("ncbi.nlm.nih.gov", SARS_COV_2_REF_URL)
        
if __name__ == '__main__':
    unittest.main()
