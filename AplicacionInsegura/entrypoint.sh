#!/bin/sh
# Esperar a que SQL Server esté listo (el script init_db.py ya tiene un sleep de 15s interno, 
# pero aquí podemos añadir lógica extra si fuera necesario)

echo "Iniciando script de entrada..."

# Ejecutar la inicialización de la base de datos
echo "Ejecutando init_db.py..."
python init_db.py

# Iniciar la aplicación Flask
echo "Iniciando aplicación Flask..."
exec flask run --host=0.0.0.0 --port=5000
