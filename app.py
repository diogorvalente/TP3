# app.py

from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)
    last_updated = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)

def recreate_db():
    """Recreates a database for testing purposes."""
    db.drop_all()
    db.create_all()

# Adicione esta parte para criar as tabelas quando o arquivo for executado diretamente
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/user/register/', methods=['POST'])
def user_register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not name or not email or not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        user = User(name=name, email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()

    if not user:
        return jsonify({'message': 'User not found'}), 403

    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'username': user.username
        })

    data = request.json
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'User information updated successfully'}), 200

@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    if request.method == 'GET':
        user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
        if not user:
            return jsonify({'message': 'User not found'}), 403

        projects = Project.query.filter_by(user_id=user.id).all()
        return jsonify([{
            'id': project.id,
            'user_id': project.user_id,
            'title': project.title,
            'creation_date': project.creation_date,
            'last_updated': project.last_updated
        } for project in projects])

    data = request.json
    title = data.get('title')
    creation_date = data.get('creation_date')
    last_updated = data.get('last_updated')

    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    try:
        project = Project(user_id=user.id, title=title, creation_date=creation_date, last_updated=last_updated)
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Project added successfully'}), 201

@app.route('/api/projects/<int:pk>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(pk):
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    project = Project.query.filter_by(id=pk, user_id=user.id).first()

    if not project:
        return jsonify({'message': 'Project not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': project.id,
            'user_id': project.user_id,
            'title': project.title,
            'creation_date': project.creation_date,
            'last_updated': project.last_updated
        })

    if request.method == 'PUT':
        data = request.json
        project.title = data.get('title', project.title)
        project.last_updated = datetime.now().strftime('%Y-%m-%d')

        try:
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        return jsonify({'message': 'Project updated successfully'}), 200

    try:
        db.session.delete(project)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Project removed successfully'}), 200

@app.route('/api/projects/<int:pk>/tasks/', methods=['GET', 'POST'])
def task_list(pk):
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    project = Project.query.filter_by(id=pk, user_id=user.id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    if request.method == 'GET':
        tasks = Task.query.filter_by(project_id=pk).all()
        return jsonify([{
            'id': task.id,
            'project_id': task.project_id,
            'title': task.title,
            'creation_date': task.creation_date,
            'completed': task.completed
        } for task in tasks])

    data = request.json
    title = data.get('title')
    creation_date = data.get('creation_date')
    completed = data.get('completed')

    existing_task = Task.query.filter_by(project_id=pk, title=title).first()
    if existing_task:
        return jsonify({'error': 'Task already exists for this project'}), 400

    try:
        task = Task(project_id=pk, title=title, creation_date=creation_date, completed=completed)
        db.session.add(task)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Task added successfully'}), 201

@app.route('/api/projects/<int:pk>/tasks/<int:task_pk>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(pk, task_pk):
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    project = Project.query.filter_by(id=pk, user_id=user.id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    task = Task.query.filter_by(id=task_pk, project_id=pk).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': task.id,
            'project_id': task.project_id,
            'title': task.title,
            'creation_date': task.creation_date,
            'completed': task.completed
        })

    if request.method == 'PUT':
        data = request.json
        task.title = data.get('title', task.title)
        task.creation_date = data.get('creation_date', task.creation_date)
        task.completed = data.get('completed', task.completed)

        try:
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        return jsonify({'message': 'Task updated successfully'}), 200

    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Task removed successfully'}), 200

@app.route('/api/messages/', methods=['GET', 'POST'])
def message_list():
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    if request.method == 'GET':
        messages = Message.query.filter((Message.sender_id == user.id) | (Message.receiver_id == user.id)).all()
        return jsonify([{
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'creation_date': message.creation_date
        } for message in messages])

    data = request.json
    sender_id = user.id
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    creation_date = data.get('creation_date')

    try:
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content, creation_date=creation_date)
        db.session.add(message)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Message sent successfully'}), 201

@app.route('/api/messages/<int:pk>/', methods=['GET', 'DELETE'])
def message_detail(pk):
    user = User.query.filter_by(username=request.authorization.username, password=request.authorization.password).first()
    if not user:
        return jsonify({'message': 'User not found'}), 403

    message = Message.query.filter((Message.id == pk) & ((Message.sender_id == user.id) | (Message.receiver_id == user.id))).first()

    if not message:
        return jsonify({'message': 'Message not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'creation_date': message.creation_date
        })

    try:
        db.session.delete(message)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Message deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)

