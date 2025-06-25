from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# 数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'student_db')

# 创建数据库连接
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 初始化数据库
def init_db():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        with open('migrations/create_tables.sql', 'r') as f:
            sql_file = f.read()
        sql_commands = sql_file.split(';')
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()

# 获取所有学生
@app.route('/students', methods=['GET'])
def get_students():
    conn = create_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students)

# 获取单个学生成绩
@app.route('/students/<string:student_id>/scores', methods=['GET'])
def get_scores(student_id):
    conn = create_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM scores WHERE student_id = %s", (student_id,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(scores)

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('username')
    password = data.get('password')

    conn = create_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s AND password = %s", (student_id, password))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return jsonify(student)
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    init_db()
    app.run(debug=True)