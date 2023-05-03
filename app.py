# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 16:09:40 2023

@author: Olga
"""
# importaciones
from flask import Flask, render_template
from flask_mysqldb import MySQL
import requests
import matplotlib.pyplot as plt
# ###################################################################
# https://api.nasa.gov/planetary/apod?api_key=dD3rq2KBZ3IonoPglO50EyY5R1ielcmBT1gbO1Jv   
# aqui estaremos haciendo una consulta a la api de la nasa con nuestra apikey que nos saldra en formato json
# ###################################################################
app = Flask(__name__)

# 1r etapa: importacion API
# funcion para poder cojer la api
def get_img():
    # Endpoint de la imagen astronómica del día de la NASA
    url='https://api.nasa.gov/planetary/apod'# parsea la info
    # Parámetros de consulta
    parametros = {'api_key': 'dD3rq2KBZ3IonoPglO50EyY5R1ielcmBT1gbO1Jv'}
    # Hacer la solicitud GET a la API de la NASA
    response = requests.get(url, params=parametros)
    data = response.json()# parsea la info en un formato JSON y lo muestra por consola
# 2n etapa: extracción de los datos
    # Imprimir los datos de la imagen del día
    print('Título:', data['title'])
    print('Fecha:', data['date'])
    print('Explicacion:', data['explanation'])
    print('URL imagen:', data['url'])
    
    return data  # retornamos la variable para poder imprimir la imagen del dia
####################################################################################################
# "bajarse" imagenes de todo un año
def img_año(fecha_inicial,fecha_final):
# llamar a los diferentes datos de la api que necesitamos
    data=get_img()
    fecha_inicial=data['start_date']
    fecha_final=data['end_date']
    titulo=data['title']
    Explicacion=data['explanation']
# encontrar de que tipo es cada imagen
    tipo= "desconocido" # variable para el almacenamiento de la imagen
    if "galaxy" in titulo.lower or 'galaxy' in Explicacion.lower():
        tipo="galaxia"
    elif "Planet" in titulo.lower or 'Planet' in Explicacion.lower():
        tipo="planeta"
    elif "Nebula" in titulo.lower or 'Nebula' in Explicacion.lower():
        tipo="Nebulosa"
    elif "Lightning" in titulo.lower or 'Lightning' in Explicacion.lower():
        tipo="Iluminacion"
    elif "Stars" in titulo.lower or 'stars' in Explicacion.lower():
        tipo="Estrella"
    elif "Eclipse" in titulo.lower or 'eclipse' in Explicacion.lower():
        tipo="Eclipse"
    elif "Storm" in titulo.lower or 'storm' in Explicacion.lower():
        tipo="Tormenta"

# insertar las imagenes en la bd
    cursor=mysql.connection.cursor()
    resultado = cursor.fetchone()
    sql = "INSERT INTO imagenes ( fecha,url,explicacion,tipo) VALUES (%s, %s, %s, %s)"
    val = (resultado['date'], resultado['url'], resultado['explanation'], tipo)
    cursor.execute(sql, val)
    resultado = cursor.fetchone()

img_año('2022-01-01', '2022-12-31')

# ###################################################################
# crear una grafica 
# ###################################################################
# enseñar la grafica con un app.route



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
# 3r etapa: visualización
####################################################################################################
@app.route('/')
def portada():
    return render_template('index.html',img=get_img())
######################
#añadir imagen cojiendo la url de la imagen/cojer la imagen del dia
@app.route('/insertar-imagen-dia')
def guardar_imagen():
    # llamar a la api
    data=get_img()
    fecha=data['date']
    url=data['url']
    Explicacion=data['explanation']
# comprobar/buscar si la img esta en la BD
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT fecha FROM imagen WHERE fecha= %s ",[fecha])
    resultado = cursor.fetchone()
# si esta mensaje de que ya esta
    if resultado:
        mensaje='La imagen ya está guardada en la BD.'
#  si no insertarla y poner el mensaje de que se a guardado
    else:
        cursor.execute("INSERT INTO imagen (fecha,url,explicacion) VALUES (%s,%s,%s)", [fecha,url,Explicacion])
        cursor.connection.commit()
        mensaje='La imagen ha sido guardada correctamente en la BD.'
        cursor.close()
    return render_template('insertar.html', mensaje=mensaje)
#####################################################
@app.route('/historial')
def historial():
    # buscar nuestra tabla para ver que hay en ella
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM imagen")
    # guardar y printar lo que haya en ella
    imagenes = cursor.fetchall()# capta el resultado de la consulta
    print(imagenes)
    cursor.close()
    # enseñar y mandar nuestro interior de la bd a un html para poder enseñarlo
    return render_template('historial.html',imagenes=imagenes)
####################################################
# @app.route('/analisis')
# def analisis():


###################################################################################################
###################################################################################################
app.run(host='Localhost', port=5000, debug=False)

