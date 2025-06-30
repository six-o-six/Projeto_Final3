from flask import Flask, jsonify, send_from_directory, request
import mysql.connector
from mysql.connector import Error

# CORREÇÃO AQUI: static_folder deve apontar para o nome real da sua pasta de frontend
app = Flask(__name__, static_folder='../PROJETO_FINAL', static_url_path='/')

# Configurações do Banco de Dados MySQL
# ATENÇÃO: Substitua 'sua_senha_mysql' pela senha do seu usuário MySQL
db_config = {
    'host': 'localhost',
    'database': 'scratch', # Nome do banco de dados que você criou
    'user': 'root',        # Geralmente 'root', ou seu usuário MySQL
    'password': 'root' # SUA SENHA AQUI
}

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

# Rota para listar todos os alunos
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

# Rota: Buscar um único aluno por ID (já existente)
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


# Rota para adicionar um novo aluno (já existente)
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

# Rota para deletar um aluno (já existente)
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

# NOVA ROTA: Editar (Atualizar) um aluno
@app.route('/alunos/edit/<int:aluno_id>', methods=['PUT'])
def edit_aluno(aluno_id):
    if request.method == 'PUT':
        aluno_data = request.get_json() # Pega os dados JSON enviados do frontend

        # Validação básica dos dados (ID e nome são cruciais para a atualização)
        if not aluno_data or not aluno_data.get('nome') or not aluno_id:
            return jsonify({'success': False, 'message': 'ID do aluno e Nome são obrigatórios'}), 400

        connection = create_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Construa a query UPDATE dinamicamente ou liste todas as colunas
                # Mapeie os campos do formulário (aluno_data) para as colunas da sua tabela 'alunos'
                # IMPORTANTE: A ordem dos valores no `values` deve corresponder à ordem dos campos na query
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
                    aluno_id # O ID do aluno que estamos atualizando (no WHERE)
                )

                cursor.execute(query, values)
                connection.commit() # Salva as alterações no banco de dados
                cursor.close()

                if cursor.rowcount > 0:
                    return jsonify({'success': True, 'message': 'Aluno atualizado com sucesso!'}), 200 # 200 OK
                else:
                    return jsonify({'success': False, 'message': 'Aluno não encontrado para atualização.'}), 404 # Not Found
            except Error as e:
                print(f"Erro ao atualizar aluno: {e}")
                connection.rollback() # Desfaz as alterações se houver erro
                return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
            finally:
                connection.close()
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)