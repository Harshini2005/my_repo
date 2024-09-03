from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# MySQL database configuration
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='flask_db',
            user='root',
            password="Root@123"
        )
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Initialize the database connection
conn = create_connection()

# Ensure the connection was successful
if conn:
    cursor = conn.cursor()
    # Create a simple table for demonstration
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# CRUD Operations

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data['name']
    email = data['email']
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO User (name, email) VALUES (%s, %s)', (name, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users', methods=['GET'])
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
def update_user(id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE User SET name = %s, email = %s WHERE id = %s', (name, email, id))
        conn.commit()
        conn.close()
        if cursor.rowcount > 0:
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users/<int:id>', methods=['DELETE'])
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
