import os
from Bio import Entrez
from Bio import SeqIO
import time

# Configuración de Entrez (Requerido por NCBI)
Entrez.email = "demo_user@edgegen.dx"  # Identificación de cortesía
Entrez.tool = "EdgeGenDx_Downloader"

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REF_DIR = os.path.join(DATA_DIR, 'references')

# IDs de Acceso de GenBank
# SARS-CoV-2 Wuhuan-Hu-1 (Completo)
COVID_ACCESSION = "NC_045512.2"
# Influenza A H3N2 (Segmento 4 - Hemaglutinina) - Cepa New York
H3N2_ACCESSION = "CY163680" 

def ensure_dirs():
    if not os.path.exists(REF_DIR):
        os.makedirs(REF_DIR)
        print(f"[Sistema] Directorio creado: {REF_DIR}")

def download_genome(accession_id, filename):
    filepath = os.path.join(REF_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"[Cache] {filename} ya existe. Saltando descarga.")
        return filepath
        
    print(f"[NCBI] Descargando {accession_id} ({filename})...")
    try:
        # Fetch desde Nucleotide database en formato FASTA
        handle = Entrez.efetch(db="nucleotide", id=accession_id, rettype="fasta", retmode="text")
        record = handle.read()
        handle.close()
        
        with open(filepath, "w") as f:
            f.write(record)
            
        print(f"[Éxito] Guardado en {filepath}")
        return filepath
    except Exception as e:
        print(f"[Error] Falló la descarga de {accession_id}: {e}")
        return None

def main():
    print("=== EdgeGen Dx: Descarga de Referencias Biológicas ===")
    ensure_dirs()
    
    # 1. SARS-CoV-2
    covid_path = download_genome(COVID_ACCESSION, "sars_cov_2_genomic.fasta")
    
    # 2. H3N2
    h3n2_path = download_genome(H3N2_ACCESSION, "h3n2_segment4.fasta")
    
    if covid_path and h3n2_path:
        print("\n[Listo] Referencias actualizadas. Ahora puedes ejecutar el entrenamiento.")
    else:
        print("\n[Aviso] Hubo errores en la descarga. Revisa tu conexión.")

if __name__ == "__main__":
    main()
