from flask import Flask, jsonify, send_from_directory, request
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash # ADIÇÃO: Para hashing de senhas
import os # ADIÇÃO: Para lidar com caminhos de arquivos

# CORREÇÃO AQUI: static_folder deve apontar para o nome real da sua pasta de frontend
app = Flask(__name__, static_folder='../PROJETO_FINAL', static_url_path='/')

# Configurações do Banco de Dados MySQL
# ATENÇÃO: Substitua 'sua_senha_mysql' pela senha do seu usuário MySQL
db_config = {
    'host': 'localhost',
    'database': 'Scratch', # Nome do banco de dados que você criou
    'user': 'root',        # Geralmente 'root', ou seu usuário MySQL
    'password': '1234' # SUA SENHA AQUI
}

# ADIÇÃO: Configuração para uploads de materiais
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads') # Pasta para salvar os arquivos de materiais
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Conexão com o banco de dados MySQL bem-sucedida!")
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
    return connection

# Rota para servir a página HTML principal (index.html)
@app.route('/')
def serve_index():
    # Isso serve o index.html da pasta frontend (que é static_folder)
    return send_from_directory(app.static_folder, 'index.html')

# Rota para servir todas as outras páginas HTML na pasta frontend
@app.route('/<path:filename>')
def serve_static_files(filename):
    # Garante que os arquivos sejam servidos da pasta frontend
    return send_from_directory(app.static_folder, filename)

# Rotas para Alunos (já existentes, mas mantidas para contexto)
@app.route('/alunos')
def get_alunos():
    connection = create_db_connection()
    alunos = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True) # Retorna resultados como dicionários
            cursor.execute("SELECT id, turma, nome, email, telefone, data_nascimento, rg, cpf, endereco, escolaridade, escola, responsavel FROM alunos")
            alunos = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar alunos: {e}")
        finally:
            connection.close()
    return jsonify(alunos)

@app.route('/alunos/<int:aluno_id>', methods=['GET'])
def get_aluno_by_id(aluno_id):
    connection = create_db_connection()
    aluno = None
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, turma, nome, email, telefone, data_nascimento, rg, cpf, endereco, escolaridade, escola, responsavel FROM alunos WHERE id = %s"
            cursor.execute(query, (aluno_id,))
            aluno = cursor.fetchone()
            cursor.close()
            if aluno:
                if aluno.get('data_nascimento'):
                    aluno['data_nascimento'] = aluno['data_nascimento'].strftime('%Y-%m-%d')
                return jsonify(aluno), 200
            else:
                return jsonify({'message': 'Aluno não encontrado!'}), 404
        except Error as e:
            print(f"Erro ao buscar aluno por ID: {e}")
            return jsonify({'message': 'Erro interno do servidor'}), 500
        finally:
            connection.close()
    return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500

@app.route('/alunos/add', methods=['POST'])
def add_aluno():
    if request.method == 'POST':
        aluno_data = request.get_json()

        if not aluno_data or not aluno_data.get('nome') or not aluno_data.get('turma'):
            return jsonify({'success': False, 'message': 'Nome e Turma são obrigatórios'}), 400

        connection = create_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO alunos (turma, nome, email, telefone, data_nascimento, rg, cpf, endereco, escolaridade, escola, responsavel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    aluno_data.get('turma'),
                    aluno_data.get('nome'),
                    aluno_data.get('email'),
                    aluno_data.get('telefone'),
                    aluno_data.get('data_nascimento'),
                    aluno_data.get('rg'),
                    aluno_data.get('cpf'),
                    aluno_data.get('endereco'),
                    aluno_data.get('escolaridade'),
                    aluno_data.get('escola'),
                    aluno_data.get('responsavel')
                )
                cursor.execute(query, values)
                connection.commit()
                cursor.close()
                return jsonify({'success': True, 'message': 'Aluno adicionado com sucesso!'}), 201
            except Error as e:
                print(f"Erro ao adicionar aluno: {e}")
                connection.rollback()
                return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
            finally:
                connection.close()
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

@app.route('/alunos/delete/<int:aluno_id>', methods=['DELETE'])
def delete_aluno(aluno_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM alunos WHERE id = %s"
            cursor.execute(query, (aluno_id,))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Aluno excluído com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Aluno não encontrado ou já excluído.'}), 404
        except Error as e:
            print(f"Erro ao deletar aluno: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

@app.route('/alunos/edit/<int:aluno_id>', methods=['PUT'])
def edit_aluno(aluno_id):
    if request.method == 'PUT':
        aluno_data = request.get_json()

        if not aluno_data or not aluno_data.get('nome') or not aluno_id:
            return jsonify({'success': False, 'message': 'ID do aluno e Nome são obrigatórios'}), 400

        connection = create_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                UPDATE alunos SET
                    turma = %s,
                    nome = %s,
                    email = %s,
                    telefone = %s,
                    data_nascimento = %s,
                    rg = %s,
                    cpf = %s,
                    endereco = %s,
                    escolaridade = %s,
                    escola = %s,
                    responsavel = %s
                WHERE id = %s
                """
                values = (
                    aluno_data.get('turma'),
                    aluno_data.get('nome'),
                    aluno_data.get('email'),
                    aluno_data.get('telefone'),
                    aluno_data.get('data_nascimento'),
                    aluno_data.get('rg'),
                    aluno_data.get('cpf'),
                    aluno_data.get('endereco'),
                    aluno_data.get('escolaridade'),
                    aluno_data.get('escola'),
                    aluno_data.get('responsavel'),
                    aluno_id
                )

                cursor.execute(query, values)
                connection.commit()
                cursor.close()

                if cursor.rowcount > 0:
                    return jsonify({'success': True, 'message': 'Aluno atualizado com sucesso!'}), 200
                else:
                    return jsonify({'success': False, 'message': 'Aluno não encontrado para atualização.'}), 404
            except Error as e:
                print(f"Erro ao atualizar aluno: {e}")
                connection.rollback()
                return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
            finally:
                connection.close()
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

# ====================================================================================================
# ADIÇÕES: NOVAS ROTAS PARA AS NOVAS TABELAS DO BANCO DE DADOS
# ====================================================================================================

# Rotas para Users (Login, Administração de Usuários)
@app.route('/users', methods=['GET'])
def get_users():
    connection = create_db_connection()
    users = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # NÃO RETORNE password_hash em uma rota GET que vai para o frontend!
            cursor.execute("SELECT id, username, full_name, role, student_id, last_login, total_logins, online_status FROM users")
            users = cursor.fetchall()
            for user in users:
                if user.get('last_login'):
                    user['last_login'] = user['last_login'].isoformat() # Formatar data para JSON
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar usuários: {e}")
        finally:
            connection.close()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    connection = create_db_connection()
    user = None
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, username, full_name, role, student_id, last_login, total_logins, online_status FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            if user:
                if user.get('last_login'):
                    user['last_login'] = user['last_login'].isoformat()
                return jsonify(user), 200
            else:
                return jsonify({'message': 'Usuário não encontrado!'}), 404
        except Error as e:
            print(f"Erro ao buscar usuário por ID: {e}")
            return jsonify({'message': 'Erro interno do servidor'}), 500
        finally:
            connection.close()
    return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500

@app.route('/users/add', methods=['POST'])
def add_user():
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')
    full_name = user_data.get('full_name')
    role = user_data.get('role')
    student_id = user_data.get('student_id')

    if not username or not password or not role:
        return jsonify({'success': False, 'message': 'Username, Password e Role são obrigatórios!'}), 400

    hashed_password = generate_password_hash(password) # ADIÇÃO: Hash da senha

    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO users (username, password_hash, full_name, role, student_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (username, hashed_password, full_name, role, student_id)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Usuário adicionado com sucesso!'}), 201
        except Error as e:
            print(f"Erro ao adicionar usuário: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor ou usuário já existe.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

@app.route('/users/edit/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    user_data = request.get_json()
    
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            set_clauses = []
            values = []
            
            if 'username' in user_data:
                set_clauses.append("username = %s")
                values.append(user_data['username'])
            if 'full_name' in user_data:
                set_clauses.append("full_name = %s")
                values.append(user_data['full_name'])
            if 'role' in user_data:
                set_clauses.append("role = %s")
                values.append(user_data['role'])
            if 'student_id' in user_data:
                set_clauses.append("student_id = %s")
                values.append(user_data['student_id'])
            if 'last_login' in user_data:
                set_clauses.append("last_login = %s")
                values.append(user_data['last_login'])
            if 'total_logins' in user_data:
                set_clauses.append("total_logins = %s")
                values.append(user_data['total_logins'])
            if 'online_status' in user_data:
                set_clauses.append("online_status = %s")
                values.append(user_data['online_status'])
            # Se a senha for alterada, hash novamente
            if 'password' in user_data and user_data['password']:
                set_clauses.append("password_hash = %s")
                values.append(generate_password_hash(user_data['password']))

            if not set_clauses:
                return jsonify({'success': False, 'message': 'Nenhum dado para atualizar.'}), 400

            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
            values.append(user_id)
            
            cursor.execute(query, tuple(values))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Usuário não encontrado para atualização.'}), 404
        except Error as e:
            print(f"Erro ao atualizar usuário: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500


@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Usuário excluído com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Usuário não encontrado.'}), 404
        except Error as e:
            print(f"Erro ao deletar usuário: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

# ADIÇÃO: Rota para login de usuário
@app.route('/login', methods=['POST'])
def login():
    credentials = request.get_json()
    username = credentials.get('username')
    password = credentials.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Nome de usuário e senha são obrigatórios.'}), 400

    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, username, password_hash, full_name, role, student_id FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user['password_hash'], password): # ADIÇÃO: Verifica senha hasheada
                # Atualiza last_login e total_logins
                update_query = "UPDATE users SET last_login = NOW(), total_logins = total_logins + 1, online_status = 'Online' WHERE id = %s"
                cursor_update = connection.cursor()
                cursor_update.execute(update_query, (user['id'],))
                connection.commit()
                cursor_update.close()

                # Retorna dados do usuário (exceto a senha hasheada)
                return jsonify({
                    'success': True,
                    'message': 'Login bem-sucedido!',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'role': user['role'],
                        'student_id': user['student_id']
                    }
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Nome de usuário ou senha incorretos.'}), 401
        except Error as e:
            print(f"Erro no login: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

# ADIÇÃO: Rota para logout de usuário (opcional, para atualizar status online)
@app.route('/logout/<int:user_id>', methods=['POST'])
def logout(user_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE users SET online_status = 'Offline' WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Logout bem-sucedido!'}), 200
        except Error as e:
            print(f"Erro no logout: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500


# Rotas para Classes
@app.route('/classes', methods=['GET'])
def get_classes():
    connection = create_db_connection()
    classes = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, title, date, status, description FROM classes ORDER BY date ASC")
            classes = cursor.fetchall()
            for cls in classes:
                if cls.get('date'):
                    cls['date'] = cls['date'].isoformat() # Formatar data para JSON
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar classes: {e}")
        finally:
            connection.close()
    return jsonify(classes)

@app.route('/classes/add', methods=['POST'])
def add_class():
    class_data = request.get_json()
    title = class_data.get('title')
    date = class_data.get('date')
    status = class_data.get('status', 'future') # Default status
    description = class_data.get('description')

    if not title or not date:
        return jsonify({'success': False, 'message': 'Título e Data são obrigatórios.'}), 400

    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO classes (title, date, status, description) VALUES (%s, %s, %s, %s)"
            values = (title, date, status, description)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Aula adicionada com sucesso!'}), 201
        except Error as e:
            print(f"Erro ao adicionar aula: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

@app.route('/classes/edit/<int:class_id>', methods=['PUT'])
def edit_class(class_id):
    class_data = request.get_json()
    
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            set_clauses = []
            values = []

            if 'title' in class_data:
                set_clauses.append("title = %s")
                values.append(class_data['title'])
            if 'date' in class_data:
                set_clauses.append("date = %s")
                values.append(class_data['date'])
            if 'status' in class_data:
                set_clauses.append("status = %s")
                values.append(class_data['status'])
            if 'description' in class_data:
                set_clauses.append("description = %s")
                values.append(class_data['description'])
            
            if not set_clauses:
                return jsonify({'success': False, 'message': 'Nenhum dado para atualizar.'}), 400

            query = f"UPDATE classes SET {', '.join(set_clauses)} WHERE id = %s"
            values.append(class_id)
            
            cursor.execute(query, tuple(values))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Aula atualizada com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Aula não encontrada.'}), 404
        except Error as e:
            print(f"Erro ao atualizar aula: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

@app.route('/classes/delete/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM classes WHERE id = %s"
            cursor.execute(query, (class_id,))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Aula excluída com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Aula não encontrada.'}), 404
        except Error as e:
            print(f"Erro ao deletar aula: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

# Rotas para Attendance Records
@app.route('/attendance', methods=['GET'])
def get_attendance_records():
    connection = create_db_connection()
    records = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # Busca registros de frequência, juntando com nomes de alunos e títulos de aula
            query = """
            SELECT ar.id, ar.student_id, a.nome as student_name, ar.class_id, c.title as class_title, ar.attendance_status, ar.recorded_at
            FROM attendance_records ar
            JOIN alunos a ON ar.student_id = a.id
            JOIN classes c ON ar.class_id = c.id
            ORDER BY ar.recorded_at DESC
            """
            cursor.execute(query)
            records = cursor.fetchall()
            for rec in records:
                if rec.get('recorded_at'):
                    rec['recorded_at'] = rec['recorded_at'].isoformat()
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar registros de frequência: {e}")
        finally:
            connection.close()
    return jsonify(records)

@app.route('/attendance/student/<int:student_id>', methods=['GET'])
def get_attendance_by_student(student_id):
    connection = create_db_connection()
    records = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT ar.id, ar.student_id, ar.class_id, c.title as class_title, c.date as class_date, ar.attendance_status, ar.recorded_at
            FROM attendance_records ar
            JOIN classes c ON ar.class_id = c.id
            WHERE ar.student_id = %s
            ORDER BY c.date ASC
            """
            cursor.execute(query, (student_id,))
            records = cursor.fetchall()
            for rec in records:
                if rec.get('recorded_at'):
                    rec['recorded_at'] = rec['recorded_at'].isoformat()
                if rec.get('class_date'):
                    rec['class_date'] = rec['class_date'].isoformat()
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar frequência do aluno: {e}")
        finally:
            connection.close()
    return jsonify(records)


@app.route('/attendance/add', methods=['POST'])
def add_attendance_record():
    record_data = request.get_json()
    student_id = record_data.get('student_id')
    class_id = record_data.get('class_id')
    attendance_status = record_data.get('attendance_status')

    if not student_id or not class_id or not attendance_status:
        return jsonify({'success': False, 'message': 'Student ID, Class ID e Status de Frequência são obrigatórios.'}), 400

    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO attendance_records (student_id, class_id, attendance_status) VALUES (%s, %s, %s)"
            values = (student_id, class_id, attendance_status)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Registro de frequência adicionado com sucesso!'}), 201
        except Error as e:
            # Lidar com UNIQUE constraint violation se já existe registro
            if e.errno == 1062: # MySQL error code for Duplicate entry
                return jsonify({'success': False, 'message': 'Registro de frequência para este aluno e aula já existe.'}), 409
            print(f"Erro ao adicionar registro de frequência: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

@app.route('/attendance/edit/<int:record_id>', methods=['PUT'])
def edit_attendance_record(record_id):
    record_data = request.get_json()
    attendance_status = record_data.get('attendance_status')

    if not attendance_status:
        return jsonify({'success': False, 'message': 'Status de Frequência é obrigatório.'}), 400
    
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE attendance_records SET attendance_status = %s WHERE id = %s"
            values = (attendance_status, record_id)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Registro de frequência atualizado com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Registro de frequência não encontrado.'}), 404
        except Error as e:
            print(f"Erro ao atualizar registro de frequência: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

@app.route('/attendance/delete/<int:record_id>', methods=['DELETE'])
def delete_attendance_record(record_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM attendance_records WHERE id = %s"
            cursor.execute(query, (record_id,))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Registro de frequência excluído com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Registro de frequência não encontrado.'}), 404
        except Error as e:
            print(f"Erro ao deletar registro de frequência: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

# Rotas para Student Overall Status
@app.route('/student_status', methods=['GET'])
def get_student_overall_status():
    connection = create_db_connection()
    statuses = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT sos.student_id, a.nome as student_name, sos.current_status, sos.presence_percentage, sos.activities_submitted_info, sos.last_activity_completed
            FROM student_overall_status sos
            JOIN alunos a ON sos.student_id = a.id
            """
            cursor.execute(query)
            statuses = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar status geral dos alunos: {e}")
        finally:
            connection.close()
    return jsonify(statuses)

@app.route('/student_status/add_or_update', methods=['POST'])
def add_or_update_student_status():
    status_data = request.get_json()
    student_id = status_data.get('student_id')
    current_status = status_data.get('current_status')
    presence_percentage = status_data.get('presence_percentage')
    activities_submitted_info = status_data.get('activities_submitted_info')
    last_activity_completed = status_data.get('last_activity_completed')

    if not student_id:
        return jsonify({'success': False, 'message': 'Student ID é obrigatório.'}), 400

    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # Use INSERT ... ON DUPLICATE KEY UPDATE para adicionar ou atualizar
            query = """
            INSERT INTO student_overall_status (student_id, current_status, presence_percentage, activities_submitted_info, last_activity_completed)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                current_status = VALUES(current_status),
                presence_percentage = VALUES(presence_percentage),
                activities_submitted_info = VALUES(activities_submitted_info),
                last_activity_completed = VALUES(last_activity_completed)
            """
            values = (student_id, current_status, presence_percentage, activities_submitted_info, last_activity_completed)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Status do aluno atualizado com sucesso!'}), 200
        except Error as e:
            print(f"Erro ao adicionar/atualizar status do aluno: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

# Rotas para Materials
@app.route('/materials', methods=['GET'])
def get_materials():
    connection = create_db_connection()
    materials = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name, file_type, file_size, upload_date, description, file_path FROM materials ORDER BY upload_date DESC")
            materials = cursor.fetchall()
            for mat in materials:
                if mat.get('upload_date'):
                    mat['upload_date'] = mat['upload_date'].isoformat()
            cursor.close()
        except Error as e:
            print(f"Erro ao buscar materiais: {e}")
        finally:
            connection.close()
    return jsonify(materials)

@app.route('/materials/upload', methods=['POST'])
def upload_material():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado.'}), 400
    
    # ADIÇÃO: Obter metadados adicionais do formulário (se existirem)
    name = request.form.get('name', file.filename)
    description = request.form.get('description', '')

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath) # Salva o arquivo no servidor

        connection = create_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO materials (name, file_type, file_size, description, file_path)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (name, file.content_type, file.content_length, description, filename)
                cursor.execute(query, values)
                connection.commit()
                material_id = cursor.lastrowid
                cursor.close()
                return jsonify({'success': True, 'message': 'Material enviado e registrado com sucesso!', 'id': material_id}), 201
            except Error as e:
                print(f"Erro ao registrar material no DB: {e}")
                connection.rollback()
                return jsonify({'success': False, 'message': 'Erro interno do servidor ao registrar material.'}), 500
            finally:
                connection.close()
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500
    return jsonify({'success': False, 'message': 'Erro no upload do arquivo.'}), 500

@app.route('/materials/download/<path:filename>', methods=['GET'])
def download_material(filename):
    # Serve o arquivo diretamente da pasta de uploads
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/materials/edit/<int:material_id>', methods=['PUT'])
def edit_material(material_id):
    material_data = request.get_json()
    
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            set_clauses = []
            values = []

            if 'name' in material_data:
                set_clauses.append("name = %s")
                values.append(material_data['name'])
            if 'description' in material_data:
                set_clauses.append("description = %s")
                values.append(material_data['description'])
            
            if not set_clauses:
                return jsonify({'success': False, 'message': 'Nenhum dado para atualizar.'}), 400

            query = f"UPDATE materials SET {', '.join(set_clauses)} WHERE id = %s"
            values.append(material_id)
            
            cursor.execute(query, tuple(values))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Material atualizado com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Material não encontrado.'}), 404
        except Error as e:
            print(f"Erro ao atualizar material: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500

@app.route('/materials/delete/<int:material_id>', methods=['DELETE'])
def delete_material(material_id):
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # Primeiro, obtenha o nome do arquivo para deletá-lo do sistema de arquivos
            cursor.execute("SELECT file_path FROM materials WHERE id = %s", (material_id,))
            material = cursor.fetchone()
            
            if material and material.get('file_path'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], material['file_path'])
                if os.path.exists(filepath):
                    os.remove(filepath) # Exclui o arquivo do servidor
                    print(f"Arquivo {filepath} excluído do servidor.")
                else:
                    print(f"Arquivo {filepath} não encontrado no servidor, mas continuará a exclusão do DB.")

            # Em seguida, exclua o registro do banco de dados
            query = "DELETE FROM materials WHERE id = %s"
            cursor.execute(query, (material_id,))
            connection.commit()
            cursor.close()
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Material excluído com sucesso!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Material não encontrado.'}), 404
        except Error as e:
            print(f"Erro ao deletar material: {e}")
            connection.rollback()
            return jsonify({'success': False, 'message': 'Erro interno do servidor.'}), 500
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)