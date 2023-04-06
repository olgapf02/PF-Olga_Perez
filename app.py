# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 16:09:40 2023

@author: Olga
"""
# importaciones
from flask import Flask, render_template
from flask_mysqldb import MySQL
import requests
# ###################################################################
# https://api.nasa.gov/planetary/apod?api_key=dD3rq2KBZ3IonoPglO50EyY5R1ielcmBT1gbO1Jv   
# aqui estaremos haciendo una consulta a la api de la nasa con nuestra apikey que nos saldra en formato json
# ###################################################################
app = Flask(__name__)

# 1r etapa: extracción de los datos
# funcion para poder cojer la api
def get_img():
    # Endpoint de la imagen astronómica del día de la NASA
    url='https://api.nasa.gov/planetary/apod'# parsea la info
    # Parámetros de consulta
    parametros = {'api_key': 'dD3rq2KBZ3IonoPglO50EyY5R1ielcmBT1gbO1Jv'}
    # Hacer la solicitud GET a la API de la NASA
    response = requests.get(url, params=parametros)
    data = response.json()# parsea la info en un formato JSON y lo muestra por consola

    # Imprimir los datos de la imagen del día
    print('Título:', data['title'])
    print('Fecha:', data['date'])
    print('Explicación:', data['explanation'])
    print('URL imagen:', data['url'])
    
    return data  # retornamos la variable para poder imprimir la imagen del dia
####################################################################################################
####################################################################################################
# mysql
# configuracion de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gaol1920'
app.config['MYSQL_DB'] = 'imagenes'
# conectarse a la BD
mysql = MySQL(app)
####################################################################################################
# rutas
# 2n etapa: visualización
####################################################################################################
@app.route('/')
def portada():
    return render_template('index.html',img=get_img())
####################################################################################################
#añadir imagen cojiendo la url de la imagen/cojer la imagen del dia
@app.route('/insertar-imagen-dia')
def guardar_imagen():
    # llamar a la api
    data=get_img()
    fecha=data['date']
    url=data['url']
# comprobar/buscar si la img esta en la BD
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT fecha FROM imagen WHERE fecha= %s ",[fecha])
    resultado = cursor.fetchone()
# si esta mensaje de que ya esta
    if resultado:
        mensaje='La imagen ya está guardada en la BD.'
#  si no insertarla y poner el mensaje de que ya esta
    else:
        cursor.execute("INSERT INTO imagen (fecha,url) VALUES (%s,%s)", [fecha,url])
        cursor.connection.commit()
        mensaje='La imagen ha sido guardada correctamente en la BD.'
        cursor.close()
    return render_template('insertar.html', mensaje=mensaje)
####################################################################################################

@app.route('/historial')
def historial():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM imagen")
    imagenes = cursor.fetchall()# capta el resultado de la consulta
    print(imagenes)
    cursor.close()
    return render_template('historial.html',imagenes=imagenes)
####################################################################################################  
app.run(host='Localhost', port=5000, debug=False)

