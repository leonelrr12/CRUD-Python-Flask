import os
from flask import Flask, session
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="guasimo.com"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']= 'db-mysql-nyc3-04501-do-user-7220305-0.b.db.ondigitalocean.com'
app.config['MYSQL_DATABASE_USER']='dbkotowa'
app.config['MYSQL_DATABASE_PASSWORD']='FtktBOEQa9UHFDPe'
app.config['MYSQL_DATABASE_DB']='sitio_flask'
app.config['MYSQL_DATABASE_PORT']=25060
mysql.init_app(app)


@app.route('/')
def inicio():
  return render_template('site/index.html')

@app.route('/libros')
def libros():
  cnn=mysql.connect()
  cursor=cnn.cursor()
  cursor.execute("SELECT * FROM libros")
  libros=cursor.fetchall()
  
  return render_template('site/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
  return render_template('site/nosotros.html')


@app.route('/admin/')
def admin_index():
  if not 'login' in session:
    return redirect('/admin/login')

  return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
  return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
  _usuario = request.form['usuario']
  _password = request.form['password']

  if _usuario == "admin" and _password == "123":
    session["login"]=True
    session["usuario"]="Administrador++"
    return redirect('/admin')

  return render_template('admin/login.html', mensaje="Error en usuario y/o contraseña.")

@app.route('/admin/cerrar')
def admin_cerrar():
  session.clear()
  return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():

  if not 'login' in session:
    return redirect('/admin/login')

  cnn=mysql.connect()
  cursor=cnn.cursor()
  cursor.execute("SELECT * FROM libros")
  libros=cursor.fetchall()
  
  return render_template('admin/libros.html', libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():
  if not 'login' in session:
    return redirect('/admin/login')

  _nombre=request.form['txtName']
  _url=request.form['txtURL']
  _archivo=request.files['txtImagen']
  tiempo=datetime.now()
  horaActual=tiempo.strftime('%Y%H%M%S')
  nuevoNombre=""
  if _archivo.filename != "":
    nuevoNombre=horaActual+"-"+_archivo.filename
    _archivo.save("templates/site/images/"+nuevoNombre)

  sql="INSERT INTO libros (nombre, imagen, url) VALUES (%s, %s, %s);" 
  datos=(_nombre, nuevoNombre, _url)
  cnn=mysql.connect()
  cursor=cnn.cursor()
  cursor.execute(sql, datos)
  cnn.commit()
  return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():
  if not 'login' in session:
    return redirect('/admin/login')

  _id=request.form['txtID']
  cnn=mysql.connect()
  cursor=cnn.cursor()

  cursor.execute("SELECT imagen FROM libros WHERE id=%s", (_id))
  row=cursor.fetchall()
  cnn.commit() 

  imagen=row[0][0]
  if imagen != "":
    if os.path.exists("templates/site/images/"+str(imagen)):
      os.unlink("templates/site/images/"+str(imagen))

  #sql="DELETE FROM libros WHERE id = %s"
  #datos=(_id)
  #cursor.execute(sql, datos)
  cursor.execute("DELETE FROM libros WHERE id = %s", (_id))
  cnn.commit()
  return redirect('/admin/libros')

@app.route('/images/<imagen>')
def images(imagen):
  return send_from_directory(os.path.join('templates/site/images'), imagen)

@app.route('/css/<archivocss>')
def css_link(archivocss):
  return send_from_directory(os.path.join('templates/site/css'), archivocss)


if __name__ == '__main__':
  app.run(debug=True)
