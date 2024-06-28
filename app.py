"""
 Flask REST application

"""
from datetime import datetime

from flask import Flask, request, jsonify, make_response
from models import Database


# ==========
#  Settings
# ==========

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
app.config['DEBUG'] = True


# ==========
#  Database
# ==========

# Creates an sqlite database in memory
db = Database(filename=':memory:', schema='schema.sql')
db.recreate()


# ===========
#  Web views
# ===========

@app.route('/')
def index():
    return app.send_static_file('index.html')


# ===========
#  API views
# ===========

@app.route('/api/user/register/', methods=['POST'])
def user_register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # Inserir novo utilizador no banco de dados
    db.execute_query('INSERT INTO user (name, email, username, password) VALUES (?, ?, ?, ?)',
                     (name, email, username, password))

    # Retornar mensagem de sucesso
    return jsonify({'message': 'Utilizador registrado com sucesso'}), 201


@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    user = db.execute_query('SELECT * FROM user WHERE username=? AND password=?', (
        request.authorization.username,
        request.authorization.password,
    )).fetchone()

    if not user:
        return jsonify({'message': 'Utilizador não encontrado'}), 403

    if request.method == 'GET':
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'username': user['username']
        })

    # Aqui removemos o elif desnecessário, já que o bloco anterior já fez um return
    data = request.json
    user['name'] = data.get('name', user['name'])
    user['email'] = data.get('email', user['email'])

    # Atualizar Utilizador no banco de dados
    db.execute_query('UPDATE user SET name=?, email=? WHERE id=?',
                     (user['name'], user['email'], user['id']))

    return jsonify({'message': 'Informações do utilizador atualizadas com sucesso'}), 200



@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    if request.method == 'GET':
        projects = db.execute_query('SELECT * FROM project WHERE user_id=?',
                                    (request.authorization.username,)).fetchall()
        return jsonify(projects)

    # Aqui removemos o elif desnecessário, já que o bloco anterior já fez um return
    data = request.json
    title = data.get('title')
    creation_date = data.get('creation_date')
    last_updated = data.get('last_updated')

    # Inserir novo projeto no banco de dados
    db.execute_query('INSERT INTO project (user_id, title, creation_date, last_updated) '
                          'VALUES (?, ?, ?, ?)',
                     (request.authorization.username, title, creation_date, last_updated))

    return jsonify({'message': 'Projeto adicionado com sucesso'}), 201



@app.route('/api/projects/<int:pk>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(pk):
    project = db.execute_query('SELECT * FROM project WHERE id=? AND user_id=?',
                               (pk, request.authorization.username)).fetchone()

    if not project:
        return jsonify({'message': 'Projeto não encontrado'}), 404

    if request.method == 'GET':
        return jsonify(project)

    if request.method == 'PUT':
        data = request.json
        project['title'] = data.get('title', project['title'])
        project['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        # Atualizar projeto no banco de dados
        db.execute_query('UPDATE project SET title=?, last_updated=? WHERE id=?',
                         (project['title'], project['last_updated'], pk))

        return jsonify({'message': 'Projeto atualizado com sucesso'}), 200

    # Se o método for DELETE, remover projeto do banco de dados
    # (Note que não há necessidade de elif, pois se o método for GET ou PUT,
    # já retornamos a resposta apropriada)
    db.execute_query('DELETE FROM project WHERE id=?', (pk,))

    return jsonify({'message': 'Projeto removido com sucesso'}), 200



@app.route('/api/projects/<int:pk>/tasks/', methods=['GET', 'POST'])
def task_list(pk):
    if request.method == 'GET':
        tasks = db.execute_query('SELECT * FROM task WHERE project_id=?', (pk,)).fetchall()
        return jsonify(tasks)
    elif request.method == 'POST':
        data = request.json
        title = data.get('title')
        creation_date = data.get('creation_date')
        completed = data.get('completed')

        #Verificar se a tarefa já existe para evitar duplicações
        existing_task = db.execute_query(
        'SELECT * FROM task WHERE project_id=? AND title=?', (pk, title)).fetchone()
        if existing_task:
            return jsonify({'error': 'Tarefa já existe para este projeto'}), 400

        # Inserir nova tarefa no banco de dados
        db.execute_query(
        'INSERT INTO task (project_id, title, creation_date, completed) VALUES (?, ?, ?, ?)',
                         (pk, title, creation_date, completed))

        return jsonify({'message': 'Tarefa adicionada com sucesso'}), 201



@app.route('/api/projects/<int:pk>/tasks/<int:task_pk>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(pk, task_pk):
    task = db.execute_query('SELECT * FROM task WHERE id=? AND project_id=?',
                            (task_pk, pk)).fetchone()

    if not task:
        return jsonify({'message': 'Tarefa não encontrada'}), 404

    if request.method == 'GET':
        return jsonify(task)
    elif request.method == 'PUT':
        data = request.json
        task['title'] = data.get('title', task['title'])
        task['creation_date'] = data.get('creation_date', task['creation_date'])
        task['completed'] = data.get('completed', task['completed'])

        # Atualizar tarefa no banco de dados
        db.execute_query('UPDATE task SET title=?,creation_date=?, completed=? WHERE id=?',
                         (task['title'], task['creation_date'], task['completed'], task_pk))

        return jsonify({'message': 'Tarefa atualizada com sucesso'}), 200
    elif request.method == 'DELETE':
        # Remover tarefa do banco de dados
        db.execute_query('DELETE FROM task WHERE id=?', (task_pk,))

        return jsonify({'message': 'Tarefa removida com sucesso'}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
