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

from Bio import SeqIO
import random

REF_DIR = os.path.join(DATA_DIR, 'references')

# Genetic Signatures (Updated for Real Data)
VIRUS_DB = {
    'covid19': {
        'name': 'SARS-CoV-2',
        'fasta': 'sars_cov_2_genomic.fasta',
        'filename': 'model_covid.tflite'
    },
    'h3n2': {
        'name': 'Influenza A (H3N2)',
        'fasta': 'h3n2_segment4.fasta',
        'filename': 'model_h3n2.tflite'
    }
}

def load_genome_sequence(filename):
    """Loads the first sequence from a FASTA file."""
    path = os.path.join(REF_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Reference file not found: {path}. Run src/data/download.py first.")
    
    # Parse FASTA
    record = next(SeqIO.parse(path, "fasta"))
    return str(record.seq).upper()

def generate_synthetic_data(target_virus, num_samples=2000):
    """
    Genera datos de entrenamiento usando Sliding Window sobre genomas reales.
    """
    encoder = DNAEncoder(method='integer', max_length=100)
    X = []
    y = []
    
    viral_data = VIRUS_DB.get(target_virus)
    if not viral_data: raise ValueError(f"Unknown target: {target_virus}")
    
    # 1. Load Target Genome
    target_full_seq = load_genome_sequence(viral_data['fasta'])
    print(f"[Train] Cargado Genoma {viral_data['name']}: {len(target_full_seq)} bases.")
    
    # 2. Identify Decoys (Other viruses)
    decoy_seqs = []
    for k, v in VIRUS_DB.items():
        if k != target_virus:
            try:
                decoy_seqs.append(load_genome_sequence(v['fasta']))
            except:
                pass # Ignore if missing
    
    print(f"[Train] Generando {num_samples} muestras reales + augmentadas...")
    
    for i in range(num_samples):
        is_target = i % 2 == 0
        
        if is_target:
            # TARGET CLASS (1)
            # Sliding Window Sampling: Pick random 100bp chunk from FULL genome
            max_start = len(target_full_seq) - 100
            start = random.randint(0, max_start)
            seq_list = list(target_full_seq[start:start+100])
            
            # Data Augmentation (Mutations)
            if random.random() < 0.5: # 50% chance of mutation
                mutation_rate = 0.05
                num_mutations = int(100 * mutation_rate)
                bases = ['A','C','G','T']
                for _ in range(num_mutations):
                    idx = random.randint(0, 99)
                    seq_list[idx] = random.choice(bases)
            
            seq = "".join(seq_list)
            label = 1
            
        else:
            # NEGATIVE CLASS (0)
            # 70% Decoy (Real different virus), 30% Random Noise
            use_decoy = (decoy_seqs and random.random() < 0.7)
            
            if use_decoy:
                # Sample from Decoy Genome
                decoy_genome = random.choice(decoy_seqs)
                max_start = len(decoy_genome) - 100
                if max_start > 0:
                    start = random.randint(0, max_start)
                    seq = decoy_genome[start:start+100]
                else:
                     # Fallback if decoy too short (unlikely for genomes)
                     seq = decoy_genome.ljust(100, 'N')[:100]
            else:
                # Random Noise
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
    
    # 5. Convert to TFLite (Float32 - No Quantization for accuracy)
    print(f"[TFLite] Convirtiendo modelo {target_virus}...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # converter.optimizations = [tf.lite.Optimize.DEFAULT] # Disabled for accuracy
    
    # def representative_dataset():
    #     for i in range(100):
    #         yield [X_train[i].astype(np.float32).reshape(1, 100)]
    #
    # converter.representative_dataset = representative_dataset
    # converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    # converter.inference_input_type = tf.int8
    # converter.inference_output_type = tf.int8
    
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
