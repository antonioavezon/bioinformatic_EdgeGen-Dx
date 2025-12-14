#!/usr/bin/env python3
import time
import os
import sys
import random

# Color codes for terminal
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Ensure path availability
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ingestion import create_dummy_fastq
    from src.inference import EdgeInference
except ImportError as e:
    print(f"{RED}[Error] No se pudieron importar los módulos necesarios: {e}{RESET}")
    sys.exit(1)

def print_banner():
    print(f"{CYAN}================================================================{RESET}")
    print(f"{CYAN}   EdgeGen Dx - Sistema de Clasificación Genómica Offline      {RESET}")
    print(f"{CYAN}   v0.1.0 MVP - Demo de Portafolio                             {RESET}")
    print(f"{CYAN}================================================================{RESET}")
    print("")

def run_demo():
    print_banner()
    
    # 1. Ingesta
    print(f"{YELLOW}[Ingesta] Preparando muestra de prueba...{RESET}")
    sample_path = create_dummy_fastq()
    time.sleep(0.5) # Efecto dramático
    
    # 2. Carga del Motor
    print(f"{YELLOW}[Sistema] Iniciando motor de inferencia (TensorFlow Lite)...{RESET}")
    try:
        engine = EdgeInference()
        print(f"{GREEN}[OK] Modelo Neural Cargado y Cuantizado (Int8).{RESET}")
    except Exception as e:
        print(f"{RED}[Fatal] Error cargando modelo: {e}{RESET}")
        print("Tip: ¿Ejecutaste 'python src/model/train.py' primero?")
        sys.exit(1)
        
    print("")
    print(f"{CYAN}---> ANALIZANDO LECTURAS DE ARQUIVO: {os.path.basename(sample_path)} <---{RESET}")
    time.sleep(1)
    
    # Simular lectura línea a línea del archivo FASTQ
    total_reads = 0
    virus_hits = 0
    
    # Leer las primeras 50 lecturas para la demo
    with open(sample_path, 'r') as f:
        lines = f.readlines()
        
    # El archivo FASTQ tiene 4 líneas por lectura.
    num_entries = len(lines) // 4
    to_process = min(20, num_entries) # Analizar 20 lecturas para que sea rápido en pantalla
    
    print(f"Procesando {to_process} lecturas de secuenciación...")
    print("-" * 60)
    print(f"{'ID LECTURA':<20} | {'PREDICCIÓN':<20} | {'TIEMPO':<10}")
    print("-" * 60)
    
    latencies = []
    
    for i in range(to_process):
        # Line 0: Header, Line 1: Specimen Sequence
        header = lines[i*4].strip()
        sequence = lines[i*4 + 1].strip()
        
        pathogen, confidence, ms = engine.predict(sequence)
        latencies.append(ms)
        
        if "Viral" in pathogen:
            virus_hits += 1
            color = RED
        else:
            color = GREEN
            
        print(f"{header:<20} | {color}{pathogen:<20}{RESET} | {ms:.2f}ms")
        time.sleep(0.1) # Pausa pequeña para que el ojo humano siga el log
        
    avg_latency = sum(latencies) / len(latencies)
    
    print("-" * 60)
    print("")
    print(f"{CYAN}=== REPORTE FINAL ==={RESET}")
    if virus_hits > (to_process * 0.3): # Si > 30% son virales
        print(f"{RED}[ALERTA BIO-PELIGRO] Se ha detectado material genético de SARS-CoV-2.{RESET}")
        print(f"Lecturas positivas: {virus_hits}/{to_process}")
    else:
        print(f"{GREEN}[NEGATIVO] Muestra limpia. No se detectaron patógenos conocidos.{RESET}")
        
    print(f"Latencia Promedio por Inferencia: {YELLOW}{avg_latency:.2f} ms{RESET}")
    print(f"Velocidad de Procesamiento: {1000/avg_latency:.0f} lecturas/segundo")
    
if __name__ == "__main__":
    run_demo()
