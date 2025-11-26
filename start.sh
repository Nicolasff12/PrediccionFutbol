#!/bin/bash
# Script de inicio para Railway

set -e  # Salir si hay algún error

# Crear directorio staticfiles si no existe (antes de cualquier operación)
echo "Creando directorio staticfiles..."
mkdir -p staticfiles
mkdir -p media

# Ejecutar migraciones (con manejo de errores)
echo "Ejecutando migraciones..."
python manage.py migrate --noinput || {
    echo "Error ejecutando migraciones. Verificando configuración de base de datos..."
    exit 1
}

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear || {
    echo "Advertencia: Error al recolectar archivos estáticos, continuando..."
}

# Verificar que el directorio existe después de collectstatic
if [ ! -d "staticfiles" ]; then
    echo "Creando directorio staticfiles después de collectstatic..."
    mkdir -p staticfiles
fi

# Obtener puerto de variable de entorno o usar 8080 por defecto
PORT=${PORT:-8080}

echo "Iniciando servidor en puerto $PORT..."

# Iniciar gunicorn
exec gunicorn prediccion_futbol.wsgi:application --bind 0.0.0.0:$PORT

