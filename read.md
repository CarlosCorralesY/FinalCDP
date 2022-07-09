# <div align="center">
<table>
    <theader>
        <tr>
            <th><img src="https://github.com/rescobedoulasalle/git_github/blob/main/ulasalle.png?raw=true" alt="EPIS" style="width:50%; height:auto"/></th>
            <th>
                <span style="font-weight:bold;">UNIVERSIDAD LA SALLE</span><br />
                <span style="font-weight:bold;">FACULTAD DE INGENIERÍAS</span><br />
                <span style="font-weight:bold;">DEPARTAMENTO DE INGENIERÍA Y MATEMÁTICAS</span><br />
                <span style="font-weight:bold;">CARRERA PROFESIONAL DE INGENIERÍA DE SOFTWARE</span>
            </th>            
        </tr>
    </theader>
    
</table>
</div>

<div align="center">
<span style="font-weight:bold;">EXAMEN FINAL VII SEMSTRE</span><br />
</div>

<table>
    <theader>
        <tr><th colspan="2">INFORMACIÓN BÁSICA</th></tr>
    </theader>
<tbody>

<tr><td>TÍTULO DE LA PRÁCTICA:</td><td>API REST</td></tr>
<tr><td colspan="2">RECURSOS:
    <ul>
    <li>Kubernetes</li>
	<li>Docker</li>
    <li>Flask</li>
    <li>Python</li>
	<li>REST</li>
    </ul>
</td>
</<tr>
<tr><td colspan="2">DOCENTES:
    <ul>
        <li>Richart Smith Escobedo Quispe  - r.escobedo@ulasalle.edu.pe</li>
    </ul>
</td>
</<tr>
</tdbody>
</table>


## OBJETIVOS Y TEMAS

### OBJETIVOS
- Crear un servicio dentor de un cluster almacenado en Kubernetes para mantenerla corriendo.
- Consumir dicho servicio.

## DESARROLLO

### DESARROLLO DEL SERVIDOR REST
- El rpimer paso es instalar nuestras dependencias.
- Instalamos el Kubernetes y su client.
  ```sh
    choco install kubectl
    choco install kubectl-cli
  ```
- Instalamos el K3d, el cual nos sirve para crear clusters
  ```sh
    choco install k3d
  ```

- Luego proseguimos con la creación de nuestro cluster.
  ```sh
    k3d cluster create --api-port 6550 -p "8081:80@loadbalancer"
  ```

#### DATA BASE
- El siguiente paso es crear la base de datos. Esto se hara en Docker.

  ```sh
    docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag
  ```
- some-mysql = el nombre de la imagen mysql
- my-secret-pw = la clave del MYSQL
- tag = la version


- mysql-secret.yaml = Archivo tipo secret para almacenar nuestra clave en base64 (esto se puede hacer en https://www.base64encode.org/). 
  ```sh
    apiVersion: v1
    kind: Secret
    metadata:
      name: mysql-pass
    type: Opaque
    data:
      password: 
  ```
 - Ejecutamos:
 ```sh
   kubectl create -f mysql-secret.yaml
 ```
 - Comprobamos:
 ```sh
   kubectl get secrets
 ```

 - mysql-pod.yaml = Contenedor para guardar los datos necesarios para el funcionamiento e ingreso a nuestra base de datos.
  ```sh
  apiVersion: v1
kind: Pod
metadata:
  name: k8s-mysql
  labels:
    name: lbl-k8s-mysql
spec:
  containers:
  - image: mysql:latest #base de datos
    name: mysql
    env:
    - name: MYSQL_ROOT_PASSWORD
      valueFrom:
        secretKeyRef:
          name: mysql-pass
          key: password
    ports:
    - name: mysql
      containerPort: 3306
      protocol: TCP
    volumeMounts:
    - name: k8s-mysql-storage
      mountPath: /var/lib/mysql
  volumes:
  - name: k8s-mysql-storage
    emptyDir: {}
  ```
- Ejecutamos:
  ```sh
   kubectl create -f mysql-pod.yaml
   ```
- Comprobamos:
	```sh
   kubectl get pod
 	```
 
-mysql-service.yaml = el servicio que mantendra corriendo o empezara a correr nuestra base de datos
  ```sh
   	apiVersion: v1
	kind: Service
	metadata:
  		name: mysql-service
  		labels:
    	name: lbl-k8s-mysql
	spec:
  		ports:
  		- port: 3306
  		selector:
    		name: lbl-k8s-mysql
    		type: ClusterIP
 ```

- Ejecutamos:
  ```sh
  kubectl create -f mysql-service.yaml
  ```
- Comprobamos:
 ```sh
  kubectl get svc
  ```

- Para editar nuestra base de datos usaremos los siguientes comandos:
   ```sh
   kubectl exec k8s-mysql -it -- bash
	mysql --user=root --password=$MYSQL_ROOT_PASSWORD
 	```


#### SERVIDOR WEB
 
 - Se trbajo con Flask, la cual es una libreria de python: 
  ```sh
   import os
from click import password_option
from flask import Flask
from flask import jsonify
from flask import request
from peewee import MySQLDatabase, IntegerField
 
MYSQL_ROOT_USER = os.getenv('MYSQL_ROOT_USER', 'root')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD', 'arczero1') #clave
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

 ```

- Creamos la imagen de nuestro server. Para esto se necesita crear un archivo Docker par decirle al docker que hacer, y un archivo con los requeremientos o extensiones que se desean
- requirements.txt :
  ```sh
    Flask

    pymysql

    peewee

    cryptography
   ```
 
- Dockerfile:
  ```sh
  FROM python:3

  WORKDIR /project

  COPY . .

  RUN pip install -r requirements.txt

  CMD ["flask", "run", "--host=0.0.0.0", "--port=8282" ]
 ```
 
- Una vez tengamos lo anterior es momento de crear la imagen y de subirla a DockerHub.
  ```sh
    docker build -t CarlosDanielCorralesYarasca/backend-final .
    docker push CarlosDanielCorralesYarasca/backend-final 
  ```

- Una vez hecho esto, se procede a crear los archivos yaml para poner en linea el server.

- config-map.yaml = donde se definaran las varibles de la base de datos y de nuestro ejecutable.
 ```sh
    apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  FLASK_APP: app.py
  MYSQL_ROOT_USER: root
  MYSQL_ROOT_PASSWORD: arczero1
  MYSQL_ROOT_HOST: '10.42.0.9' #"%"
  MYSQL_ROOT_PORT: "3306"
  MYSQL_ROOT_DB: bdnew
  FLASK_APP_PORT: "8282"
  ```
- Ejecutamos:
 ```sh
    kubectl apply -f config-map.yaml
 ```
- web-application-deployment.yaml = el archivo deploy para que la app dentro de la imagen funcione

 ```sh
   apiVersion: apps/v1

kind: Deployment

metadata:

  labels:

    app: web-application 

  name: web-application 

spec:

  replicas: 1

  strategy:

    type: Recreate

  selector:

    matchLabels:

      app: web-application

  template:

    metadata:

      labels:

        app: web-application

    spec:

      containers:

      - image: CarlosDanielCorralesYarasca/backend-final:latest #imagen

        name: web-application

        imagePullPolicy: Always        

        resources:

          limits:

            cpu: "0.6"

            memory: "512Mi"

          requests:

            cpu: "0.3"

            memory: "256Mi"

        env:

          - name: FLASK_APP

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: FLASK_APP

          - name: MYSQL_ROOT_USER

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: MYSQL_ROOT_USER

          - name: MYSQL_ROOT_PASSWORD

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: MYSQL_ROOT_PASSWORD

          - name: MYSQL_ROOT_HOST

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: MYSQL_ROOT_HOST

          - name: MYSQL_ROOT_PORT

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: MYSQL_ROOT_PORT

          - name: MYSQL_ROOT_DB

            valueFrom:

              configMapKeyRef:

                name: app-config

                key: MYSQL_ROOT_DB
 ```
 
- Ejecutamos: 
 ```sh
    kubectl get deployment
  ```
- comprobamos:  
	```sh
    kubectl apply -f web-application-deployment.yaml
  ```

- Cremos el service
  ```sh
    kubectl create service clusterip web-application — tcp=80:8282
  ```
 
- web-application-ingress.yaml = permite el acceso desde el cluster.

  ```sh
    apiVersion: networking.k8s.io/v1

    kind: Ingress

    metadata:

      name: web-application

      annotations:

        ingress.kubernetes.io/ssl-redirect: "false"

    spec:

      rules:

      - http:

          paths:

          - path: /

            pathType: Prefix

            backend:

              service:

                name: web-application

                port:

                  number: 80
  ```
  
- Ejecutamos:
  ```sh
     kubectl apply -f web-application-ingress.yaml
  ```
- La aplicación llegada a este punto deberia de estar funcionando correctamente  
#


## REFERENCIAS
- https://styde.net/crear-una-base-de-datos-en-mysql-mariadb/
- https://blog.devgenius.io/how-to-deploy-rest-api-application-using-mysql-on-the-kubernetes-cluster-4c806de1a48
- https://hub.docker.com/_/mysql

