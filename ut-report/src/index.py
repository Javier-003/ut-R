from crypt import methods
import hashlib
import bcrypt
from flask import Flask, render_template, request, redirect, session, url_for,Response,flash
import os

#from tkinter import *
#from tkinter import messagebox as MessageBox
import conexion as db


# Configurar la aplicacion para ser ejecutado
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, "src", "templates")

# Declaramos la variable de ejecucion  de la aplicacion
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7'

def encriptar_password(password):
    password_bytes = password.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(password_bytes)
    hash_hex = sha256.hexdigest()
    return hash_hex[:10]


####principal####
@app.route('/',methods=['GET'])
def home():
    insertObjeto = []
    if 'logueado' in session and session['logueado']:
            
        return render_template('index1.html', datos=insertObjeto)
    else:
        return redirect('/login')
    
####registro e inicio de sesion###
@app.route('/login', methods=["GET","POST"])
def login():
   if request.method == 'POST':
        correo = request.form.get('txtcorreo')
        contraseña = request.form.get('txtcontraseña')

        # Aquí asumimos que "connection" es un objeto de conexión MySQL ya configurado
        cursor = db.conexion.cursor()
        cursor.execute("SELECT * FROM usuario WHERE correo = %s AND contraseña = %s", (correo, contraseña))
        account = cursor.fetchone()
        cursor.close()

        if account:
            session['logueado'] = True
            session['id_rol'] = account[0]

            if session['id_rol']== 1:
                return redirect('/administador')
            else:
                return redirect('/')
        else:
            # Si no se encuentra la cuenta, muestra el mensaje como un modal
            mensaje = "Correo o Contraseña erronea"
            tipo_mensaje = "error"
            return render_template("inicioS.html", mensaje=mensaje, tipo_mensaje=tipo_mensaje)
   return render_template("inicioS.html")

@app.route('/registro', methods=['POST'])
def registro():
    # importamos las variables desde el form del index.htlm
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    contraseña = request.form["contraseña"]
    rol = request.form["rol"]
    if nombre and correo and contraseña and rol:
     cursor = db.conexion.cursor()
      # Verificar si el correo electrónico ya existe en la base de datos
     sql_verificar_correo = "SELECT COUNT(*) FROM usuario WHERE correo = %s"
     cursor.execute(sql_verificar_correo, (correo,))
     num_registros = cursor.fetchone()[0]

     if num_registros > 0:
            mensaje = "Correo ya en uso"
            tipo_mensaje = "error"
            return redirect(url_for("login", mensajeError=mensaje, tipo_mensaje=tipo_mensaje))
     else:
        sql = """INSERT INTO usuario (nombre,correo,contraseña,id_rol) values (%s,%s,%s,%s)"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (nombre, correo,contraseña,rol)
    cursor.execute(sql, datos)
    mensaje = "Registro hecho de manera exitosa"
    tipo_mensaje = "exito"
    db.conexion.commit()
    return redirect(url_for("login",mensaje=mensaje,tipo_mensaje=tipo_mensaje))

@app.route('/logout')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect('/login') # Redirige al inicio de sesión

############admin#####################
@app.route('/ListaUsuarios')
def ListaUsuarios():
    cursor = db.conexion.cursor()
    
    # Realiza una consulta para obtener los datos de los usuarios y roles
    cursor.execute("SELECT usuario.id, usuario.nombre, usuario.correo, usuario.contraseña, rol.descripción FROM usuario JOIN rol ON usuario.id_rol = rol.id ")
    datosDB = cursor.fetchall()

    # convertir los datos a diccionario y encriptar la contraseña antes de mostrarla
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        registro_dict = dict(zip(columnName, registro))
        registro_dict['contraseña'] = encriptar_password(registro_dict['contraseña'])
        insertObjeto.append(registro_dict)

    # Cierra la conexión con la base de datos
    cursor.close()
    return render_template('listaUsuarios.html', data=insertObjeto)



@app.route('/ListaReportes')
def listaReportes():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT reporte.id, reporte.usuario, reporte.fechar, reporte.tipo, reporte.descripcion, estado.estatus FROM reporte JOIN estado ON reporte.id_estado = estado.idEstado WHERE reporte.id_estado IN ('1', '2', '3','4')")
    datosDB = cursor.fetchall()
    # convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName, registro)))   
    cursor.close()
    return render_template('listaReportes.html',data=insertObjeto)

@app.route('/listaReportesS')
def listaReportesS():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT reporte.id, reporte.usuario, reporte.fechar, reporte.tipo, reporte.descripcion, estado.estatus FROM reporte JOIN estado ON reporte.id_estado = estado.idEstado WHERE id_estado IN ('5','6','7')")
    datosDB = cursor.fetchall()
    # convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName, registro)))   
    cursor.close()
    return render_template('listaReportesS.html',data=insertObjeto)

@app.route('/insertUsuario', methods=['POST'])
def insertUsuario():
    # importamos las variables desde el form del index.htlm
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    contraseña = request.form["contraseña"]
    rol = request.form["rol"]
    if nombre and correo and contraseña and rol:
     cursor = db.conexion.cursor()
     sql = """INSERT INTO usuario (nombre,correo,contraseña,id_rol) values (%s,%s,%s,%s)"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (nombre, correo,contraseña,rol,)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("ListaUsuarios"))

@app.route('/eliminarUsuario/<string:id>')
def eliminarUsuario(id):
      
    cursor = db.conexion.cursor()
    sql = """ DELETE FROM usuario WHERE id=%s"""
        
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (id,)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("ListaUsuarios"))

@app.route('/administador')
def administrador():
    
    return render_template('admin.html')
    


@app.route('/insertReporte', methods=['POST'])
def insertReporte():
    # importamos las variables desde el form del index.htlm
    fecha = request.form["fecha"]
    tipo = request.form["tipo"]
    descripcion = request.form["descripcion"]
    estados = request.form["estadoU"]
    if fecha and tipo:
     cursor = db.conexion.cursor()
     sql = """INSERT INTO reporte (fechar,tipo,descripcion,estado) values (%s,%s,%s,%s)"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (fecha, tipo,descripcion,estados)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("listaReportes"))


@app.route('/eliminarReporte/<string:id>')
def eliminarReporte(id):
      
    cursor = db.conexion.cursor()
    sql = """ DELETE FROM reporte WHERE id=%s"""
        
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (id,)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("listaReportes"))

@app.route('/actualizarReporte/<string:id>',methods=['POST'])
def actualizarPais(id):
    estado=request.form["estado"]
    if estado:
        cursor = db.conexion.cursor()
        sql="""UPDATE reporte
        SET id_estado=%s
        WHERE id=%s"""
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos = (estado,id)
    cursor.execute(sql, datos)
    db.conexion.commit()
    return redirect(url_for("listaReportes")) 


#######usuario###
@app.route('/listaReportesU')
def listaReportesU():
    cursor = db.conexion.cursor()
    cursor.execute("""SELECT reporte.fechar, reporte.tipo, reporte.descripcion, estado.estatus FROM reporte JOIN estado ON reporte.id_estado = estado.idEstado """)
    datosDB = cursor.fetchall()
    # convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName, registro)))   
    cursor.close()
    return render_template('listaReportesU.html',data=insertObjeto)

@app.route('/usuarioReporte', methods=['POST'])
def usuarioReporte():
    nombre = request.form["nombre"]
    fecha = request.form["fecha"]
    tipo = request.form["tipo"]
    descripcion = request.form["descripcion"]
    estado=1
    if fecha and tipo and descripcion:
      cursor = db.conexion.cursor()
      sql = """INSERT INTO reporte (usuario,fechar,tipo,descripcion,id_estado) values (%s,%s,%s,%s,%s)"""
    else:
        return redirect(url_for("home"))
    # declaramos a "datos" como una variable de tipo tupla para mandar la información
    datos=(nombre,fecha,tipo,descripcion,estado)
    cursor.execute(sql,datos)
    db.conexion.commit()
    return render_template("index1.html")






if __name__ == "__main__":
    app.run(debug=True, port=4000)
