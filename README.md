# EdgeGen Dx: Clasificación Genómica en el Borde

> **Estado**: Prototipo / Demo Educativa  
> **Autor**: Antonio  
> **Objetivo**: Inferencia de patógenos en tiempo real sin conexión a internet.

## 🧬 Descripción del Proyecto
EdgeGen Dx es una prueba de concepto que simula un dispositivo médico portátil ("Point-of-Care"). Su misión es analizar secuencias genómicas crudas (lecturas de ADN/ARN) directamente en un entorno local (como esta PC), identificando la presencia de virus como SARS-CoV-2 o MERS en milisegundos, sin depender de la nube.

Este proyecto demuestra la intersección entre **Bioinformática**, **Inteligencia Artificial (Deep Learning)** y **Computación de Alto Rendimiento**.

## 🚀 Características Principales
*   **100% Offline**: Privacidad total de los datos médicos.
*   **IA Comprimida**: Usa modelos CNN optimizados con TensorFlow Lite.
*   **Flujo Completo**: Desde la ingesta de archivos `.fastq` hasta el reporte clínico.

## 📦 Estructura del Proyecto
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

### Prerrequisitos
*   **Sistema Operativo**: Linux (probado en Fedora 43).
*   **Hardware**: CPU estándar (Soporte opcional para GPU NVIDIA para entrenamiento).
*   **Python**: 3.10+

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
