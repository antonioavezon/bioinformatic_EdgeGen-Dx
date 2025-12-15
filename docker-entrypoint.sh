#!/bin/bash

# Aplicar migraciones (si usas DB)
echo "Aplicando migraciones..."
python web_interface/manage.py migrate

# Recolectar estáticos (si fuera necesario, para demo simple no hace falta tanto lio)
# python web_interface/manage.py collectstatic --noinput

# Iniciar servidor Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn --chdir web_interface web_interface.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
