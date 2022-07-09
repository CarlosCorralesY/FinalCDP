import os
from click import password_option
from flask import Flask
from flask import jsonify
from flask import request
from peewee import MySQLDatabase, IntegerField
 
MYSQL_ROOT_USER = os.getenv('MYSQL_ROOT_USER', 'root')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD', 'caramelito123') #clave
MYSQL_ROOT_HOST = os.getenv('MYSQL_ROOT_HOST', 'localhost')
MYSQL_ROOT_PORT = os.getenv('MYSQL_ROOT_PORT', '3306')
MYSQL_ROOT_DB = os.getenv('MYSQL_ROOT_DB', 'bdnew') #base de datos
FLASK_APP_PORT = os.getenv('FLASK_APP_PORT', '8282')
 
db = MySQLDatabase(database=MYSQL_ROOT_DB, user=MYSQL_ROOT_USER, password=MYSQL_ROOT_PASSWORD,
                    host=MYSQL_ROOT_HOST, port=int(MYSQL_ROOT_PORT))
 
app = Flask(__name__)
 
cursor = db.cursor() 


@app.route('/login', methods=['POST'])
def login():
    params = {
        'name' : request.json['name'],
        'password' : request.json['password']
    }
    query = """SELECT id from users where name=%(name)s and password=%(password)s"""
    cursor.execute(query,params)
    data = cursor.fetchone()
    return jsonify(data)    


@app.route('/new_usuario', methods=['POST'])
def new():
    params = {
        'name' : request.json['name'],
        'lastname' : request.json['lastname'],
        'password' : request.json['password']
    }
    query= """INSERT INTO users (name,lastname, password) 
                    VALUES (%(name)s,%(lastname)s ,%(password)s);"""
    cursor.execute(query,params)
    return jsonify("hecho")


 ###################################Datos_db##################################################################


@app.route('/update_datos', methods=['PUT'])
def update_datos():
    params = {
        'title' : request.json['title'],
        'body' : request.json['body'],
        'id' : request.json['id']
    }
    query="""UPDATE datos SET title =%(title)s, body=%(body)s WHERE id =%(id)s"""
    cursor.execute(query,params)
    return jsonify("hecho")   

@app.route('/delete_datos', methods=['DELETE'])
def delete_datos():
    params = {
        'id' : request.json['id']
    }
    query="""DELETE from datos where id=%(id)s"""
    cursor.execute(query,params)
    return jsonify("hecho")   

@app.route('/new_datos', methods=['POST'])
def new_datos():
    params = {
        'title' : request.json['title'],
        'body' : request.json['body'],
        'id_user' : int(request.json['id_user'])
    }
    query= """INSERT INTO datos (title, body,id_user) 
                VALUES (%(title)s ,%(body)s,%(id_user)s );"""

    cursor.execute(query,params)
    return jsonify("hecho")   

@app.route('/get_datos', methods=['GET'])
def get_datos():
    cursor.execute("SELECT id,title,body from datos where id_user="+request.json['id'])
    rv = cursor.fetchall()
    data=[]
    content ={}
    for result in rv:
        content = {'id': result[0], 'title': result[1], 'body': result[2]}
        data.append(content)
        content = {}
    return jsonify(data)   

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(FLASK_APP_PORT))