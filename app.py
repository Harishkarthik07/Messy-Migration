from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, name, email FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users]), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data['password'])
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (data['name'], data['email'], hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not (name and email):
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User updated"}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"User {user_id} deleted"}), 200

@app.route('/search', methods=['GET'])
def search_users():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name query param required"}), 400

    conn = get_db_connection()
    users = conn.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (f'%{name}%',)).fetchall()
    conn.close()
    return jsonify([dict(user) for user in users]), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ('email', 'password')):
        return jsonify({"error": "Missing email or password"}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], data['password']):
        return jsonify({"status": "success", "user_id": user['id']}), 200
    return jsonify({"status": "failed"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
