import tensorflow as tf
from tensorflow.keras import layers, models

def create_genomic_cnn(input_length=100, num_classes=2):
    """
    Crea un modelo de Deep Learning CNN 1D optimizado para clasificación de secuencias.
    
    Args:
        input_length (int): Longitud de la secuencia de ADN (e.g., 100bp).
        num_classes (int): Número de patógenos a clasificar (2: Virus vs Humano).
        
    Returns:
        tf.keras.Model: Modelo compilado.
    """
    model = models.Sequential([
        # Capa de entrada: Esperamos vectores one-hot o integer
        # Si usamos Integer encoding, necesitamos Embedding layer.
        # Asumiremos Integer encoding para este diseño (1 channel input si es raw int, o embedding).
        # Para ser robustos con la clase DNAEncoder (Integer mode), usamos Embedding.
        # Vocab size = 5 (0=Pad, 1=A, 2=C, 3=G, 4=T)
        layers.Input(shape=(input_length,)),
        layers.Embedding(input_dim=5, output_dim=16, input_length=input_length),
        
        # 1. Feature Extraction (Convolutional Layers)
        layers.Conv1D(filters=32, kernel_size=12, activation='relu'),
        layers.MaxPooling1D(pool_size=4),
        
        layers.Conv1D(filters=16, kernel_size=8, activation='relu'),
        layers.MaxPooling1D(pool_size=4),
        
        # 2. Classification Head
        layers.Flatten(),
        layers.Dense(16, activation='relu'),
        layers.Dropout(0.5), # Regularización
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    model = create_genomic_cnn()
    model.summary()
