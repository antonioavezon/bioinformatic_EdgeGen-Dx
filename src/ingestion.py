import os
import urllib.request
import gzip
import shutil

# Dataset de prueba: SARS-CoV-2 (Wuhan) - Submuestra pequeña para demo
# Usamos una URL simulada o un endpoint que permita rango de bytes para no bajar 5GB
# Para efectos de esta demo MVP, descargaremos una referencia pequeña o simularemos el FASTQ
# si no tenemos acceso a internet rápido o herramientas SRA instaladas.
# En un entorno real ideal, usaríamos `fastq-dump` de sra-toolkit.

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
REF_DIR = os.path.join(DATA_DIR, 'references')

SARS_COV_2_REF_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/858/895/GCF_009858895.2_ASM985889v3/GCF_009858895.2_ASM985889v3_genomic.fna.gz"

def ensure_directories():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(REF_DIR, exist_ok=True)

def download_reference_genome():
    """Descarga el genoma de referencia de SARS-CoV-2"""
    target_path = os.path.join(REF_DIR, 'sars_cov_2.fna.gz')
    if os.path.exists(target_path):
        print(f"[Check] Referencia encontrada: {target_path}")
        return target_path
    
    print(f"[Download] Descargando genoma de referencia SARS-CoV-2...")
    try:
        urllib.request.urlretrieve(SARS_COV_2_REF_URL, target_path)
        print("[OK] Descarga completada.")
        return target_path
    except Exception as e:
        print(f"[Error] Falló la descarga: {e}")
        return None

def create_dummy_fastq(filename="sample_covid.fastq", num_reads=1000):
    """
    Crea un archivo FASTQ sintético para probar el flujo sin descargar GBs de datos.
    Contiene fragmentos aleatorios mezclados con secuencias virales simuladas.
    """
    target_path = os.path.join(RAW_DIR, filename)
    if os.path.exists(target_path):
        print(f"[Check] Muestra encontrada: {target_path}")
        return target_path

    print(f"[Ingestion] Generando muestra sintética {filename} con {num_reads} lecturas...")
    
    # Secuencia "Viral" simulada (fragmento de Spike protein)
    # real: ATGTTC...
    viral_signature = "ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACACGTGGTGTTTATTACCCTGACAAAGTTTTCAGATCCTCAGTTTTACATTCAACTCAGGACTTGTTCTTACCTTTCTTTTCCAATGTTAKTTGGTTCCATGCTATACATGTCTCTGGGACCAATGGTACTAAGAGGTTTGATAACCCTGTCCTACCATTTAATGATGGTGTTTATTTTGCTTCCACTGAGAAGTCTAACATAATAAGAGGCTGGATTTTTGGTACTACTTTAGATTCGAAGACCCAGTCCCTACTTATTGTTAATAACGCTACTAATGTTGTTATTAAAGTCTGTGAATTTCAATTTTGTAATGATCCATTTTTGGGTGTTTATTAC"
    
    with open(target_path, 'w') as f:
        for i in range(num_reads):
            # Formato FASTQ:
            # @Header
            # Sequence
            # +
            # Quality
            header = f"@SEQ_ID_{i} GRP_1"
            # 50% probabilidad de ser viral para la demo
            is_viral = (i % 2 == 0)
            
            if is_viral:
                # Tomar un slice random de la firma viral
                start = (i * 5) % len(viral_signature)
                seq = viral_signature[start:start+100]
                if len(seq) < 100: seq = seq.ljust(100, 'A')
            else:
                # Ruido aleatorio (simulando humano/bacterias no target)
                import random
                bases = ['A', 'C', 'G', 'T']
                seq = "".join([random.choice(bases) for _ in range(100)])
            
            quality = "I" * 100 # Dummy quality score (high quality)
            
            f.write(f"{header}\n{seq}\n+\n{quality}\n")
    
    print(f"[OK] Muestra generada exitosamente.")
    return target_path

if __name__ == "__main__":
    ensure_directories()
    download_reference_genome()
    create_dummy_fastq()
