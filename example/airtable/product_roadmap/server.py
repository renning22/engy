
import os
import sqlite3
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__, static_folder='.')
CORS(app)
app.config['DATABASE'] = 'project_management.db'

# Basic Authentication
def check_auth(username, password):
    return username == 'admin' and password == 'password'

def authenticate():
    return jsonify({'message': 'Authentication required.'}), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Database setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Helper functions
def dict_from_row(row):
    return dict(zip(row.keys(), row))

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def calculate_progress(items):
    total = len(items)
    completed = sum(1 for item in items if item['status'] == 'Completed')
    return int((completed / total) * 100) if total > 0 else 0

# API Routes
@app.route('/projects', methods=['GET'])
@requires_auth
def get_projects():
    db = get_db()
    cursor = db.execute('SELECT * FROM projects')
    projects = [dict_from_row(row) for row in cursor.fetchall()]
    
    for project in projects:
        cursor = db.execute('SELECT * FROM stages WHERE project_id = ?', (project['id'],))
        stages = [dict_from_row(row) for row in cursor.fetchall()]
        project['progress'] = calculate_progress(stages)
    
    return jsonify(projects)

@app.route('/projects', methods=['POST'])
@requires_auth
def create_project():
    data = request.json
    if not all(key in data for key in ('name', 'description', 'start_date', 'end_date')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['start_date']) or not validate_date(data['end_date']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    if data['start_date'] > data['end_date']:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO projects (name, description, start_date, end_date) VALUES (?, ?, ?, ?)',
        (data['name'], data['description'], data['start_date'], data['end_date'])
    )
    db.commit()
    
    return jsonify({'id': cursor.lastrowid, **data}), 201

@app.route('/projects/<int:project_id>', methods=['GET'])
@requires_auth
def get_project(project_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if project is None:
        return jsonify({'error': 'Project not found'}), 404
    
    project = dict_from_row(project)
    
    cursor = db.execute('SELECT * FROM stages WHERE project_id = ?', (project_id,))
    stages = [dict_from_row(row) for row in cursor.fetchall()]
    project['stages'] = stages
    project['progress'] = calculate_progress(stages)
    
    return jsonify(project)

@app.route('/projects/<int:project_id>', methods=['PUT'])
@requires_auth
def update_project(project_id):
    data = request.json
    if not all(key in data for key in ('name', 'description', 'start_date', 'end_date')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['start_date']) or not validate_date(data['end_date']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    if data['start_date'] > data['end_date']:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    db = get_db()
    db.execute(
        'UPDATE projects SET name = ?, description = ?, start_date = ?, end_date = ? WHERE id = ?',
        (data['name'], data['description'], data['start_date'], data['end_date'], project_id)
    )
    db.commit()
    
    return jsonify(data)

@app.route('/projects/<int:project_id>', methods=['DELETE'])
@requires_auth
def delete_project(project_id):
    db = get_db()
    db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    db.commit()
    
    return '', 204

@app.route('/projects/<int:project_id>/stages', methods=['GET'])
@requires_auth
def get_stages(project_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM stages WHERE project_id = ?', (project_id,))
    stages = [dict_from_row(row) for row in cursor.fetchall()]
    
    for stage in stages:
        cursor = db.execute('SELECT * FROM tasks WHERE stage_id = ?', (stage['id'],))
        tasks = [dict_from_row(row) for row in cursor.fetchall()]
        stage['progress'] = calculate_progress(tasks)
    
    return jsonify(stages)

@app.route('/projects/<int:project_id>/stages', methods=['POST'])
@requires_auth
def create_stage(project_id):
    data = request.json
    if not all(key in data for key in ('name', 'description', 'start_date', 'end_date', 'status')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['start_date']) or not validate_date(data['end_date']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    if data['start_date'] > data['end_date']:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO stages (project_id, name, description, start_date, end_date, status) VALUES (?, ?, ?, ?, ?, ?)',
        (project_id, data['name'], data['description'], data['start_date'], data['end_date'], data['status'])
    )
    db.commit()
    
    return jsonify({'id': cursor.lastrowid, **data}), 201

@app.route('/stages/<int:stage_id>', methods=['PUT'])
@requires_auth
def update_stage(stage_id):
    data = request.json
    if not all(key in data for key in ('name', 'description', 'start_date', 'end_date', 'status')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['start_date']) or not validate_date(data['end_date']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    if data['start_date'] > data['end_date']:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    db = get_db()
    db.execute(
        'UPDATE stages SET name = ?, description = ?, start_date = ?, end_date = ?, status = ? WHERE id = ?',
        (data['name'], data['description'], data['start_date'], data['end_date'], data['status'], stage_id)
    )
    db.commit()
    
    return jsonify(data)

@app.route('/stages/<int:stage_id>', methods=['DELETE'])
@requires_auth
def delete_stage(stage_id):
    db = get_db()
    db.execute('DELETE FROM stages WHERE id = ?', (stage_id,))
    db.commit()
    
    return '', 204

@app.route('/stages/<int:stage_id>/tasks', methods=['GET'])
@requires_auth
def get_tasks(stage_id):
    db = get_db()
    cursor = db.execute('SELECT * FROM tasks WHERE stage_id = ?', (stage_id,))
    tasks = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(tasks)

@app.route('/stages/<int:stage_id>/tasks', methods=['POST'])
@requires_auth
def create_task(stage_id):
    data = request.json
    if not all(key in data for key in ('name', 'description', 'deadline', 'status')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['deadline']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO tasks (stage_id, name, description, deadline, status) VALUES (?, ?, ?, ?, ?)',
        (stage_id, data['name'], data['description'], data['deadline'], data['status'])
    )
    db.commit()
    
    return jsonify({'id': cursor.lastrowid, **data}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@requires_auth
def update_task(task_id):
    data = request.json
    if not all(key in data for key in ('name', 'description', 'deadline', 'status')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_date(data['deadline']):
        return jsonify({'error': 'Invalid date format'}), 400
    
    db = get_db()
    db.execute(
        'UPDATE tasks SET name = ?, description = ?, deadline = ?, status = ? WHERE id = ?',
        (data['name'], data['description'], data['deadline'], data['status'], task_id)
    )
    db.commit()
    
    return jsonify(data)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@requires_auth
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    
    return '', 204

@app.route('/upcoming-deadlines', methods=['GET'])
@requires_auth
def get_upcoming_deadlines():
    db = get_db()
    today = datetime.now().date()
    week_from_now = today + timedelta(days=7)
    
    cursor = db.execute('''
        SELECT t.*, s.name as stage_name, p.name as project_name
        FROM tasks t
        JOIN stages s ON t.stage_id = s.id
        JOIN projects p ON s.project_id = p.id
        WHERE t.deadline BETWEEN ? AND ?
        ORDER BY t.deadline
    ''', (today.isoformat(), week_from_now.isoformat()))
    
    upcoming_tasks = [dict_from_row(row) for row in cursor.fetchall()]
    return jsonify(upcoming_tasks)

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    app.run(host='localhost', port=5120, debug=True)
