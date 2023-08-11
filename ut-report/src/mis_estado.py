from flask import Flask, render_template, request, redirect, url_for
import os
from tkinter import *
from tkinter import messagebox as MessageBox
import conexion as db


# Configurar la aplicacion para ser ejecutado
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, "src", "templates")

# Declaramos la variable de ejecucion  de la aplicacion
app = Flask(__name__, template_folder=template_dir)


@app.route('/estado')
def estado():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT * FROM estado")
    datosDB = cursor.fetchall()
    # convertir los datos a diccionario
    estados = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        estados.append(dict(zip(columnName, registro)))   
    cursor.close()
    return render_template('admin.html',data1=estados)


@app.route ('/estadoid')
def estadoid():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT idEstado,estatus FROM estado")
    datosDB = cursor.fetchall()
    cursor.close()
    return render_template('admin.html',datosDB=datosDB)
    


@app.route('/insertEstado', methods=['POST'])
def insertEstado():
    # importamos las variables desde el form del index.htlm 
    estado= request.form["estado"]
    cursor = db.conexion.cursor()
    sql = """INSERT INTO estado (estatus)
        values (%s)"""
   
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (estado,)
    cursor.execute(sql,datos)
    db.conexion.commit()
    return redirect(url_for("administrador"))

@app.route('/actualizarEstado/<string:idEstado>',methods=['POST'])
def actualizarEstado(id):
    estado=request.form["estados"]
    if estado:
        cursor = db.conexion.cursor()
        sql="""UPDATE estado
        SET estatus=%s
        WHERE idEstado=%s"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (estado,id)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("administrador"))  


@app.route('/eliminarEstado/<string:idEstado>')
def eliminarEstado(id):
    resultado = MessageBox.askokcancel(
        "eliminar..." "¿Estás seguro de eliminar el registro?"
    )
    if resultado == True:
        cursor = db.conexion.cursor()
        sql = """ DELETE FROM estado WHERE idEstado=%s"""
        
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (id,)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("administrador"))
if __name__ == "__main__":
    app.run(debug=True, port=5000)