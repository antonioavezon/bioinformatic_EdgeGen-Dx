import os
import random
from Bio import SeqIO
import sys

# Add src path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
REF_DIR = os.path.join(DATA_DIR, 'references')

def load_genome_random_chunk(filename, length=100):
    path = os.path.join(REF_DIR, filename)
    if not os.path.exists(path):
        return None
    
    try:
        record = next(SeqIO.parse(path, "fasta"))
        seq = str(record.seq).upper()
        if len(seq) < length:
            return seq.ljust(length, 'N')
        
        start = random.randint(0, len(seq) - length)
        return seq[start:start+length]
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def generate_random_dna(length=100):
    return "".join([random.choice(['A','C','G','T']) for _ in range(length)])

def main():
    print("=== MUESTRAS DE PRUEBA PARA WEB DEMO ===\n")
    
    # 1. SARS-CoV-2
    print("🦠 SARS-CoV-2 (Copiar en Web):")
    for i in range(1, 3):
        chunk = load_genome_random_chunk("sars_cov_2_genomic.fasta")
        if not chunk: chunk = "AUTO_GENERATED_FALLBACK_" + generate_random_dna(80) # Fallback
        print(f"Muestra {i}:\n{chunk}\n")
        
    # 2. Influenza H3N2
    print("🦠 Influenza H3N2 (Copiar en Web):")
    for i in range(1, 3):
        chunk = load_genome_random_chunk("h3n2_segment4.fasta")
        if not chunk: chunk = "AUTO_GENERATED_FALLBACK_" + generate_random_dna(80)
        print(f"Muestra {i}:\n{chunk}\n")
        
    # 3. Sana (Ruido/Clean)
    print("✅ Sana / Humana / Ruido (Copiar en Web):")
    for i in range(1, 3):
        chunk = generate_random_dna(100)
        print(f"Muestra {i}:\n{chunk}\n")

if __name__ == "__main__":
    main()
