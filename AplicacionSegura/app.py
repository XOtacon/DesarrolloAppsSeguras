import os
from flask import Flask, request, render_template, redirect, url_for, session
import pymssql

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_para_el_demo'

def get_db_connection():
    # Se obtienen las variables de entorno configuradas en el docker-compose.yml o archivo .env
    conn = pymssql.connect(
        server=os.getenv('DB_SERVER'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return conn

@app.route('/')
def index():
    session.pop('user', None)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SEGURIDAD: Consulta parametrizada para prevenir inyección SQL
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    print(f"[*] Ejecutando Consulta parametrizada sobre la tabla users.") 
    
    try:
        # Pymssql maneja la interpolación de los parámetros de forma segura
        cursor.execute(query, (username, password))
        user = cursor.fetchone() # Fetches un tuple
        conn.close()
        
        if user:
            # Asumimos que username es la columna en el índice 1 basado en init_db.py
            session['user'] = user[1] 
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Credenciales inválidas, intente nuevamente.")
    except pymssql.Error as e:
        conn.close()
        # Ocultar errores de SQL directamente al usuario para prevenir Error-Based SQLi
        # Loggear el error internamente y mostrar un mensaje genérico
        print(f"[*] Error interno de base de datos en login: {e}")
        return render_template('index.html', error="Ocurrió un error de conexión, intente nuevamente.")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
        
    search_query = request.args.get('search', '')
    users = []
    error_msg = None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_query:
        # SEGURIDAD: Consulta parametrizada con LIKE. 
        # El comodín % se agrega al parámetro, no a la consulta SQL.
        query = "SELECT id, username, email, phone FROM users WHERE username LIKE %s"
        search_param = f"%{search_query}%"
        print(f"[*] Ejecutando Búsqueda parametrizada.") 
        try:
            cursor.execute(query, (search_param,))
            users = cursor.fetchall()
        except pymssql.Error as e:
            print(f"[*] Error interno de base de datos en búsqueda: {e}")
            error_msg = "Ocurrió un error al realizar la búsqueda."
    else:
        # Consulta por defecto segura si no hay búsqueda
        cursor.execute("SELECT id, username, email, phone FROM users")
        users = cursor.fetchall()
        
    conn.close()
    return render_template('dashboard.html', username=session['user'], users=users, search_query=search_query, error=error_msg)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("Iniciando aplicación web Segura en puerto 5001...")
    app.run(debug=True, port=5001)
