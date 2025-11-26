#!/bin/bash
# Script de inicio para Railway

# Crear directorio staticfiles si no existe
mkdir -p staticfiles

# Ejecutar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Obtener puerto de variable de entorno o usar 8080 por defecto
PORT=${PORT:-8080}

# Iniciar gunicorn
exec gunicorn prediccion_futbol.wsgi:application --bind 0.0.0.0:$PORT

