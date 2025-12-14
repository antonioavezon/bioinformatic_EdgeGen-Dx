# EdgeGen Dx: Clasificación Genómica en el Borde

> **Estado**: Prototipo / Demo Educativa  
> **Autor**: Antonio  
> **Objetivo**: Inferencia de patógenos en tiempo real sin conexión a internet.

# EdgeGen Dx - Portable Genomic Analyzer (Experimental)

> [!WARNING]
> **Plataforma Experimental de Estudio**: Este software es un prototipo para investigación y educación en bioinformática y Edge AI. **NO** está certificado para uso clínico ni diagnóstico médico real.

**EdgeGen Dx** es una prueba de concepto de un dispositivo de análisis genómico portátil ("Point-of-Care") capaz de detectar patógenos en tiempo real utilizando Inteligencia Artificial acelerada por GPU, sin depender de la nube.

## 🧬 Características Principales
*   **Detección Multi-Patógeno**: Soporte para **SARS-CoV-2 (COVID-19)** e **Influenza A (H3N2)**.
*   **Inferencia en el Borde (Edge AI)**: Ejecuta modelos CNN cuantizados (TFLite) localmente.
*   **Aceleración GPU**: Optimizado para GPUs NVIDIA (RTX 4060) mediante TensorFlow/CUDA.
*   **Interfaz Profesional**: Dashboard Web (Django) con simulación de dispositivo médico.
## 🧠 Detalles Técnicos del Modelo (AI Engine)
El "cerebro" de EdgeGen Dx consta de dos redes neuronales convolucionales (CNN) independientes, especializadas por patógeno.

### Arquitectura del Modelo
*   **Tipo**: 1D Convolutional Neural Network (CNN).
*   **Entrada**: Fragmentos de ADN de 100 pares de bases (bp), codificados numéricamente.
*   **Capas**: Conv1D (Extracción de características espaciales) -> MaxPooling -> Flatten -> Dense (Clasificación).
*   **Optimizador**: Adam | **Loss**: Binary Crossentropy.

### Entrenamiento y Datos
*   **Fuente de Datos**: Los modelos se entrenaron con **datos sintéticos** generados a partir de genomas de referencia oficiales (NCBI):
    *   *SARS-CoV-2*: S-gene (Spike protein).
    *   *H3N2*: Hemagglutinin (HA) gene.
*   **Estrategia de Entrenamiento**:
    *   **Hard Negative Mining**: Para evitar falsos positivos, el modelo de COVID-19 conoce secuencias de H3N2 (y viceversa) etiquetadas explícitamente como "Negativas". Esto fuerza a la red a aprender diferencias estructurales finas y no solo distinguir "orden vs caos".
    *   **Aceleración**: Entrenado localmente usando **NVIDIA RTX 4060** (cuDNN/CUDA) en <10 segundos por modelo.
*   **Formato Final**: Modelos exportados a **TensorFlow Lite (Int8 Quantized)** para inferencia de ultra-baja latencia (<10ms) en CPUs modestas.

## 🔮 Próximos Pasos (Roadmap v2.0)
*   [ ] **Datos Reales**: Reemplazar generador sintético con pipeline de limpieza para archivos FASTQ crudos de Oxford Nanopore (MinION).
*   [ ] **Base de Datos Viral**: Ampliar a Dengue, Zika y Ébola.
*   [ ] **Visualización Genómica**: Gráfico de cobertura para mostrar qué parte exacta del virus fue detectada.
*   [ ] **Hardware IoT**: Despliegue físico en Raspberry Pi 5 + Coral Edge TPU.

## 🤝 Créditos
Desarrollado por **Antonio Avezon**.
*Versión 1.0.0 - 2025*
*   **Privacidad Total**: Todo el procesamiento es offline; la data genética nunca sale del dispositivo.

##  Despliegue en Otro Equipo (Soporte GPU)

Este proyecto está configurado para aprovechar aceleración por hardware (NVIDIA GPU). Al mover el código a otro computador, ten en cuenta:

### 1. Requisitos de Hardware
*   **GPU NVIDIA**: Computability > 5.0 (ej. RTX 3060, 4060, A100).
*   **Drivers**: Drivers de NVIDIA instalados en el sistema operativo host (Linux/Windows).

### 2. Gestión de Modelos (.tflite)
Los modelos de Inteligencia Artificial (`data/models/*.tflite`) son generados localmente.
*   **Opción A (Recomendada - Re-entrenamiento)**: Ejecutar el script de entrenamiento en el nuevo equipo. Esto verifica que la GPU funciona correctamente y genera modelos optimizados para esa arquitectura.
    ```bash
    ./venv_gpu/bin/python src/model/train.py --target all
    ```
*   **Opción B (Copiar Archivos)**: Si solo deseas ejecutar la demo sin entrenar, puedes copiar manualmente la carpeta `data/models/` del equipo original. **Nota**: Git ignora estos archivos binarios por defecto para mantener el repositorio ligero.

### 3. Instalación Limpia
Nunca copies la carpeta `venv_gpu`. Crea un entorno limpio en el nuevo equipo:
```bash
# Crear entorno
python3.12 -m venv venv_gpu

# Instalar dependencias con soporte CUDA
./venv_gpu/bin/pip install "tensorflow[and-cuda]"
./venv_gpu/bin/pip install -r requirements.txt
```

## �📦 Estructura del Proyecto
```text
EdgeGen-Dx/
├── data/               # Almacenamiento de secuencias genómicas
├── src/                # Código fuente
│   ├── ingestion.py    # Descarga de muestras públicas (SRA)
│   ├── preprocessing/  # Limpieza y codificación de ADN (k-mers)
│   ├── model/          # Entrenamiento y conversión TFLite
│   └── inference.py    # Motor de clasificación
├── demo.py             # Script maestro para demostración (CLI)
└── requirements.txt    # Dependencias del proyecto
```

## 🛠️ Requisitos e Instalación

### Requisitos del Sistema
*   **Sistema Operativo**: Linux (Recomendado Fedora/Ubuntu) o Windows (WSL2).
*   **Python**: Versión **3.12** (Crítico para soporte TensorFlow GPU).
*   **GPU (Opcional)**: NVIDIA RTX/GTX con drivers instalados (para entrenamiento acelerado).
*   **Memoria RAM**: 8GB mínimo.

### Instalación
1.  Clonar el repositorio:
    ```bash
    git clone https://github.com/antonioavezon/bioinformatic_EdgeGen-Dx.git
    cd bioinformatic_EdgeGen-Dx
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## 📊 Estrategia de Datos
Este proyecto utiliza datos genómicos reales y públicos del **European Nucleotide Archive (ENA)** y **NCBI SRA**. 

El sistema está diseñado para trabajar con:
1.  **Datos Crudos (Input)**: Archivos `.fastq` que contienen lecturas de secuenciación sucias (mezcla humano + virus).
    *   *Dataset COVID-19*: `SRR10971381` (Wuhan, 2019).
    *   *Dataset MERS*: `SRR1192017`.
2.  **Datos de Referencia**: Genomas completos para entrenamiento (`NC_045512.2` para SARS-CoV-2).

> **Nota**: Aunque el script `demo.py` descarga sub-muestras automáticamente para facilitar la prueba, los usuarios avanzados pueden descargar los datasets completos usando herramientas como `sra-toolkit`:
> `fastq-dump --split-files SRR10971381`

## 🖥️ Interfaz Web (Dispositivo Médico)
Se crea una **vista con Django**, la cual actúa como un Dashboard de Dispositivo Médico en tiempo real.
*   **Tecnología**: Django 4.0 + HTML5/CSS3 (Diseño Oscuro Profesional).
*   **Funcionalidad**:
    *   Carga de muestras (`.fastq`) simuladas o reales.
    *   Visualización de cada lectura clasificada en tiempo real.
    *   Gráfico de latencia y nivel de confianza de la IA.
    *   **Alerta Bio-Peligro**: Notificación visual inmediata si se detecta SARS-CoV-2.
*   **Acceso**: `http://localhost:8000/`

## ▶️ Uso (Demo CLI)
Para ejecutar una simulación completa de análisis:

```bash
python demo.py
```

El sistema descargará automáticamente una muestra pequeña de prueba, procesará las lecturas y emitirá un veredicto diagnóstico en pantalla.

## 🗺️ Hoja de Ruta (Roadmap)

> Estado actual: **Fase 1 - Inicialización Completa**

| Estado | Tarea | Descripción |
| :---: | :--- | :--- |
| ✅ | **Definición** | Alcance, viabilidad y estrategia de datos definida. |
| ✅ | **Estructura** | Skeleton del proyecto y documentación inicial (README). |
| ⏳ | **Ingesta** | Script para descarga automática de muestras virales (SRA). |
| ⏳ | **Pre-proceso** | Algoritmo de limpieza y tokenización (k-mers) para ADN. |
| ⏳ | **Modelado** | Diseño y entrenamiento de CNN 1D para clasificación. |
| ⏳ | **Edge AI** | Conversión del modelo a formato TFLite (Int8 Quantization). |
| ⏳ | **Demo** | Integración final en `demo.py` para uso fácil.

---
*Este proyecto es una iniciativa educativa para demostrar capacidades técnicas en el análisis de datos biológicos.*
