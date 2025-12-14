import os
import sys
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inference import EdgeInference

# Secuencias de prueba (Las mismas dadas al usuario)
SEQ_COVID = "ATTAAAGGTTTATACCTTCCCAGGTAACAAACCAACCAACTTTCGATCTCTTGTAGATCT"
SEQ_H3N2 = "ATGAAGACCATCATTGCTTTGAGCTACATTTTCTGTCTGGCTCTCGGCCAAGACCTTCCAGGAAATGACAACAGCACAGCAACGCTGTGCCTGGGACACC"
SEQ_CLEAN = "CGTACGTAGCTAGCTAGCTGATCGATGCTAGCTAGCTAGCATCGATCGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCAGTCGATCGTAGC"

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'models')

def test_covid_model_specificity():
    model_path = os.path.join(MODELS_DIR, 'model_covid.tflite')
    if not os.path.exists(model_path):
        pytest.skip("Modelo COVID no encontrado - saltando prueba de integración real")
        
    engine = EdgeInference(model_path=model_path)
    
    # 1. Debe detectar COVID
    label, conf, _ = engine.predict(SEQ_COVID)
    assert "Viral" in label, f"Falso Negativo: COVID model falló en detectar COVID. Confianza: {conf}"
    
    # 2. NO debe detectar H3N2 (Debe ser negativo)
    label, conf, _ = engine.predict(SEQ_H3N2)
    assert "Clean" in label or "Negativo" in label, f"Falso Positivo: COVID model detectó H3N2 accidentalmente. Confianza: {conf}"

    # 3. NO debe detectar Ruido
    label, conf, _ = engine.predict(SEQ_CLEAN)
    assert "Clean" in label, f"Falso Positivo: COVID model detectó Ruido. Confianza: {conf}"

def test_h3n2_model_specificity():
    model_path = os.path.join(MODELS_DIR, 'model_h3n2.tflite')
    if not os.path.exists(model_path):
        pytest.skip("Modelo H3N2 no encontrado - saltando prueba de integración real")
        
    engine = EdgeInference(model_path=model_path)
    
    # 1. Debe detectar H3N2
    label, conf, _ = engine.predict(SEQ_H3N2)
    assert "Viral" in label, f"Falso Negativo: H3N2 model falló en detectar H3N2. Confianza: {conf}"
    
    # 2. NO debe detectar COVID
    label, conf, _ = engine.predict(SEQ_COVID)
    assert "Clean" in label or "Negativo" in label, f"Falso Positivo: H3N2 model detectó COVID accidentalmente. Confianza: {conf}"

    # 3. NO debe detectar Ruido
    label, conf, _ = engine.predict(SEQ_CLEAN)
    assert "Clean" in label, f"Falso Positivo: H3N2 model detectó Ruido. Confianza: {conf}"
