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
import pandas as pd
import json
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
    response = requests.get(url, parametros)
    data = response.json()# parsea la info en un formato JSON y lo muestra por consola
# 2n etapa: extracción de los datos
    # Imprimir los datos de la imagen del día
    print('Título:', data['title'])
    print('Fecha:', data['date'])
    print('Explicacion:', data['explanation'])
    print('URL imagen:', data['url'])
    
    return data  # retornamos la variable para poder imprimir la imagen del dia
####################################################################################################
# mysql
####################################################################################################
# nos conectaoms a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gaol1920'
app.config['MYSQL_DB'] = 'imagenes'
# conectarse a la BD
mysql = MySQL(app)
####################################################################################################
# rutas
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
##########################################################################################################
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
################################################################
@app.route('/imagenes-año')
def get_img_ano():
    # Endpoint de la imagen astronómica del día de la NASA
    url='https://api.nasa.gov/planetary/apod'# parsea la info
    # Parámetros de consulta
    key = "dD3rq2KBZ3IonoPglO50EyY5R1ielcmBT1gbO1Jv"
    # extracción de los datos
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    # Hacer la solicitud GET a la API de la NASA
    response = requests.get(url,{'api_key': key, 'start_date': start_date, 'end_date': end_date})
    # print(response.json()) 

# crearemos una lista para guardar los diferentes tipos que tienen las imagenes recojidas de la api
    lista_imagenes = []
    tipo = "desconocido"
    for data in response.json():
            if "galaxy" in data['title'].lower() or 'galaxy' in data['explanation'].lower():
                tipo="galaxia"
            elif "Planet" in data['title'].lower() or 'Planet' in data['explanation'].lower():
                tipo="planeta"
            elif "Nebula" in data['title'].lower() or 'Nebula' in data['explanation'].lower():
                tipo="Nebulosa"
            elif "Lightning" in data['title'].lower() or 'Lightning' in data['explanation'].lower():
                tipo="Iluminacion"
            elif "Stars" in data['title'].lower() or 'stars' in data['explanation'].lower():
                tipo="Estrella"
            elif "Eclipse" in data['title'].lower() or 'eclipse' in data['explanation'].lower():
                tipo="Eclipse"
            elif "Storm" in data['title'].lower() or 'storm' in data['explanation'].lower():
                tipo="Tormenta"
                # despues una vez teniendo nuestra lista lo transformaremos a un diccionario
            imagenes_dicc = {
                    "title": data["title"],
                    "date": data["date"],
                    "explanation": data["explanation"],
                    "url": data["url"],
                    "tipo": tipo
                }  
            # luego diremos que la lista creada es igual al formateo del diccionario
            lista_imagenes.append(imagenes_dicc) 
            # esto nos servira para printar todas las imagenes pedidas en un año en un formato json
            # for image in lista_imagenes:
            #     print(json.dumps(image)) 
##########################
    # aqui creamos un dataframe a partir de las columnas que queremos y con los datos recogidos en la api
    df = pd.DataFrame(lista_imagenes, columns=["title", "date", "explanation", "url", "tipo"])
    # print(df)

    # escriviremos un archivo csv para tener el df mas manejable.
    # df.to_csv('imagenes-año.csv', index=False)

    # por ultimo en este render daremos una variable para que printe nuestro df en el html
    return render_template('fotos_ano.html',lista =df.to_html())
###################################################################################################
# enseñar la grafica con un app.route
@app.route('/grafica')
def grafica():
    df = pd.read_csv('imagenes-año.csv')
    # Calcular el recuento de cada tipo de imagen
    conteo_tipos = df["tipo"].value_counts()

    # Creacion de la  gráfica de barras
    fig, ax = plt.subplots()
    ax.bar(conteo_tipos.index, conteo_tipos.values)

    # Personalizacion de la gráfica
    ax.set_title("Tipos de imágenes en el año")
    ax.set_xlabel("Tipo de imagen")
    ax.set_ylabel("Cantidad")

    # Guardar la gráfica como archivo PNG
    plt.savefig('grafica.png')

    # Cerrar la figura
    plt.close()
    # En este ejemplo, la línea plt.savefig('grafica.png') guarda la gráfica en un archivo llamado "grafica.png" en el directorio actual.

    return render_template('grafica.html')


###################################################################
app.run(host='Localhost', port=5000, debug=False)

###################################################################################################
# mejoras
# crear una grafica de cada mes
#cojer cada mes y enseñar su grafica  con un formulario