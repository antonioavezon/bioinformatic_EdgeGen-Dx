import numpy as np

class DNAEncoder:
    """
    Codificador de secuencias de ADN para modelos de Deep Learning.
    Soporta:
    1. One-Hot Encoding: A->[1,0,0,0], T->[0,0,0,1], etc.
    2. Integer Encoding: A->1, C->2, G->3, T->4
    3. K-mer Tokenization (MVP simple: 4-mers).
    """
    
    def __init__(self, method='integer', max_length=100):
        self.method = method
        self.max_length = max_length
        self.mapping = {'A': 1, 'C': 2, 'G': 3, 'T': 4, 'N': 0}

    def encode(self, sequence):
        """
        Convierte una cadena de texto ADN en un array numérico.
        """
        sequence = sequence.upper().strip()
        # Truncar o padding
        if len(sequence) > self.max_length:
            sequence = sequence[:self.max_length]
        
        if self.method == 'integer':
            return self._integer_encoding(sequence)
        elif self.method == 'onehot':
            return self._onehot_encoding(sequence)
        else:
            raise ValueError(f"Método {self.method} no soportado aún.")

    def _integer_encoding(self, seq):
        # Convertir a lista de enteros, pad con 0 si es necesario
        encoded = [self.mapping.get(base, 0) for base in seq]
        padding = [0] * (self.max_length - len(encoded))
        return np.array(encoded + padding, dtype=np.int8)

    def _onehot_encoding(self, seq):
        # Shape: (max_length, 4)
        # A=0, C=1, G=2, T=3 in 0-indexed vectors usually, but here we used 1-4 mappping.
        # Let's map A->0, C->1, G->2, T->3 for standard one-hot index
        base_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        
        onehot = np.zeros((self.max_length, 4), dtype=np.float32)
        for i, base in enumerate(seq):
            if base in base_map:
                onehot[i, base_map[base]] = 1.0
        return onehot

if __name__ == "__main__":
    # Test rápido
    encoder = DNAEncoder(max_length=10)
    seq = "ACGTTAGCA"
    print(f"Secuencia: {seq}")
    print(f"Encoded (Integer): {encoder.encode(seq)}")
    
    encoder_oh = DNAEncoder(method='onehot', max_length=10)
    print(f"Encoded (One-Hot):\n{encoder_oh.encode(seq)}")
