from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key for JWT
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure value
jwt = JWTManager(app)

# MySQL database configuration
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='flask_auth_db',
            user='root',
            password="Root@123"
        )
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Initialize the database connection and create table if not exists
conn = create_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# User registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO User (name, email, password) VALUES (%s, %s, %s)', 
                           (name, email, hashed_password))
            conn.commit()
            conn.close()
            return jsonify({"message": "User registered successfully"}), 201
        except Error as e:
            conn.close()
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "Database connection failed"}), 500

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE email = %s', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user[3], password):  # user[3] is the hashed password
            # Create JWT token
            access_token = create_access_token(identity=user[0], expires_delta=datetime.timedelta(hours=1))
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    else:
        return jsonify({"error": "Database connection failed"}), 500

# Protected route that requires JWT
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({"message": f"Welcome, user {current_user_id}!"}), 200

# CRUD Operations with JWT protection

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO User (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User')
        rows = cursor.fetchall()
        conn.close()
        users = []
        for row in rows:
            users.append({"id": row[0], "name": row[1], "email": row[2]})
        return jsonify(users), 200
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE id = %s', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            user = {"id": row[0], "name": row[1], "email": row[2]}
            return jsonify(user), 200
        else:
            return jsonify({"message": "User not found"}), 404
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE User SET name = %s, email = %s, password = %s WHERE id = %s', 
                       (name, email, hashed_password, id))
        conn.commit()
        conn.close()
        if cursor.rowcount > 0:
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM User WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        if cursor.rowcount > 0:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    else:
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
