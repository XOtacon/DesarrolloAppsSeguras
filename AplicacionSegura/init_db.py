import os
import pymssql
import time

# Función para esperar a que la base de datos esté lista
def wait_for_db():
    server = os.getenv('DB_SERVER', 'db')
    user = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', 'SqlServer2026**')
    
    print(f"[*] Esperando a SQL Server en {server}...")
    while True:
        try:
            conn = pymssql.connect(
                server=server,
                user=user,
                password=password,
                database='master',
                login_timeout=5
            )
            conn.close()
            print("[+] SQL Server está listo.")
            break
        except Exception:
            print("[.] SQL Server aún no responde, reintentando en 2 segundos...")
            time.sleep(2)

wait_for_db()

# Carga de variables para la creación
server = os.getenv('DB_SERVER')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

# Conectar a la base de datos 'master' par crear la nuestra
conn = pymssql.connect(
    server=server,
    user=user,
    password=password,
    database='master'
)
conn.autocommit(True) # Requerido para crear bases de datos
cursor = conn.cursor()

print("Creando base de datos 'asignacion3' si no existe...")
try:
    cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'asignacion3') CREATE DATABASE asignacion3")
except pymssql.Error as e:
    print(f"Error al crear la base de datos: {e}")

conn.close()

# Ahora conectar a la nueva base de datos para crear la tabla
print("Conectando a la base de datos asignada para crear tabla e insertar datos...")
conn = pymssql.connect(
    server=server,
    user=user,
    password=password,
    database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Crear tabla 'users'
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' and xtype='U')
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(50),
        role VARCHAR(50) DEFAULT 'user',
        secret_notes VARCHAR(MAX)
    )
''')

# Limpiar datos existentes por si acaso
cursor.execute('DELETE FROM users')

# Insertar datos de prueba
dummy_users = [
    ('admin', 'admin123', 'admin@webapp.com', '8888-8888', 'admin', 'Super secret server backup password: M@sterKey!999'),
    ('alice', 'alice_pass', 'alice@webapp.com', '1234-5678', 'user', 'My dog is named fluffy.'),
    ('bob', 'password123', 'bob@webapp.com', '8765-4321', 'user', 'Note to self: change password next month.'),
    ('charlie', 'qwerty', 'charlie@webapp.com', '1111-2222', 'user', 'PIN de la tarjeta: 1234')
]

cursor.executemany('''
    INSERT INTO users (username, password, email, phone, role, secret_notes)
    VALUES (%s, %s, %s, %s, %s, %s)
''', dummy_users)

conn.commit()
conn.close()

print("Base de datos inicializada exitosamente.")
print("Datos de prueba creados en SQL Server local.")
