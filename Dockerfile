
# Usar base ligera de Python
FROM python:3.12-slim

# Evitar archivos .pyc y buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (build-essential para compilar librerías si hace falta)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar el código del proyecto
COPY . /app/

# Crear directorios necesarios para los modelos si no existen (aunque se copian con el código)
RUN mkdir -p data/models data/raw data/references

# Exponer puerto 8000 (interno del contenedor)
EXPOSE 8000

# Script de entrada
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
