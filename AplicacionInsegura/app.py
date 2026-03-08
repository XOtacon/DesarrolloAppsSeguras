from flask import Flask, request, render_template, redirect, url_for, session
import pymssql

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_para_el_demo'

def get_db_connection():
    # NOTA: Al ser un ejercicio, se deja la contraseña en texto plano!!
    conn = pymssql.connect(
        server='ec2-100-25-145-67.compute-1.amazonaws.com', # Base de datos en AWS
        user='sa',
        password='SqlServer2026**', 
        database='asignacion3'
    )
    return conn

@app.route('/')
def index():
    session.pop('user', None)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # VULNERABLE SQL QUERY (SQL Injection usando concatenación)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"[*] Ejecutando Consulta: {query}") # Útil para consola/demo
    
    try:
        cursor.execute(query)
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
        # Mostrar errores de SQL directamente (útil en clases para entender los ataques Error-Based SQLi)
        return render_template('index.html', error=f"Error en BD: {e}")

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
        # SECURE SQL QUERY (Parameterized query prevents SQL Injection)
        query = "SELECT id, username, email, phone FROM users WHERE username LIKE %s"
        search_param = f"%{search_query}%"
        print(f"[*] Ejecutando Consulta Parametrizada: {query} with param {search_param}") 
        try:
            cursor.execute(query, (search_param,))
            users = cursor.fetchall()
        except pymssql.Error as e:
            error_msg = f"Error en consulta: {e}"
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
    print("Iniciando aplicación web vulnerable en puerto 5000...")
    app.run(debug=True, port=5000)
