#!/bin/sh
echo "Iniciando script de entrada (Seguro)..."

# Ejecutar la inicialización de la base de datos
echo "Ejecutando init_db.py..."
python init_db.py

# Iniciar la aplicación Flask
echo "Iniciando aplicación Flask..."
exec flask run --host=0.0.0.0 --port=5001
