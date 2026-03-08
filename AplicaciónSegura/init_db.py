import pymssql
import time

print("Esperando a que la base de datos SQL Server inicie (esto puede tomar 15-30 segundos)...")
time.sleep(15) # Dar tiempo al contenedor db de iniciar

# Conectar a la base de datos 'master' por defecto para poder crear nuestra base de datos
conn = pymssql.connect(server='db', user='sa', password='SqlServer2026**', database='master')
conn.autocommit(True) # Requerido para crear bases de datos
cursor = conn.cursor()

print("Creando base de datos 'asignacion3' si no existe...")
try:
    cursor.execute("CREATE DATABASE asignacion3")
except pymssql.Error as e:
    print(f"La base de datos posiblemente ya existe: {e}")

conn.close()

# Ahora conectar a la nueva base de datos para crear la tabla
print("Conectando a 'asignacion3' para crear tabla e insertar datos...")
conn = pymssql.connect(server='db', user='sa', password='SqlServer2026**', database='asignacion3')
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
