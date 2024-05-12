from flask import Flask, render_template, url_for, redirect, request, flash
from flask_mysqldb import MySQL
from datetime import datetime
from config import config, mail_username, mail_password
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
import os

#Models
from models.model_user import ModelUser

#Entities
from models.entities.user import User

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'saucem.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'saucem'
app.config['MYSQL_PASSWORD'] = 'cslMSQL2024'
app.config['MYSQL_DB'] = 'saucem$jlrdb'

#app.config['MAIL_SERVER'] = 'c1351055.ferozo.com'
#app.config['MAIL_PORT'] = '465'
#app.config['MAIL_USE_SSL'] = 'True'
#app.config['MAIL_USERNAME'] = mail_username
#app.config['MAIL_PASSWORD'] = mail_password

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USE_SSL'] = 'True'
app.config['MAIL_USERNAME'] = 'saucem@gmail.com'
app.config['MAIL_PASSWORD'] = 'oxtomykgwzfjwube'


dbconnection = MySQL(app)
mail = Mail(app)
folder = os.path.join('mysite', 'static','images','upload')
app.config['FOLDER'] = folder

app.config['SECRET_KEY'] = '34323b759c5cac08a2adf7bf0ed9a53d10940e18946b04627e763aecf1228f14'
csrf = CSRFProtect(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
  return ModelUser.get_by_id(dbconnection,id)

@app.route('/')
def home():
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY id DESC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('index.html', categories = importedCategories, vehicles = importedVehicles)

@app.route('/showall/<int:id>')
def showall(id):
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY id DESC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  sqlSentence = "SELECT * FROM category WHERE id = " + str(id)
  cur.execute(sqlSentence)
  selectCategory = cur.fetchall()
  selectedCategory = selectCategory[0]

  return render_template('showall.html', category = selectedCategory, categories = importedCategories, vehicles = importedVehicles)

@app.route('/detail/<int:id>', methods=['GET', 'POST'])
def detail(id):
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle WHERE id = " + str(id)
  cur.execute(sqlSentence)
  selectVehicle = cur.fetchall()
  selectedVehicle = selectVehicle[0]

  sqlSentence = "SELECT * FROM vehicle ORDER BY id DESC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('detail.html', categories = importedCategories, vehicles = importedVehicles, vehicle = selectedVehicle)

@app.route('/contact/<origin>', methods=['GET', 'POST'])
def contact(origin):
  if request.method == 'POST':
    if origin == 'detail':
      id = request.form['id']
      cur = dbconnection.connection.cursor()
      sqlSentence = 'SELECT * FROM vehicle WHERE id = ' + str(id)
      cur.execute(sqlSentence)
      fetched = cur.fetchall()
      vehicle = fetched[0]
      domain = vehicle[1]
      subjectDetail = f'por el dominio {domain}'
    else:
      subjectDetail = 'desde la página principal'

    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    message = request.form.get('message')
    verification = request.form.get('human')
    if verification == '7':
      msgSentence = Message(subject=f'Mensaje recibido de {name} {subjectDetail}', body=f'Nombre: {name}\nTeléfono: {phone}\nEmail: {email}\n\n\nConsulta: {message}', sender=mail_username, recipients=['ventas@joseluisrizzo.com'])
      mail.send(msgSentence)
      flash('Su consulta ha sido enviada con éxito. Nos pondremos en contacto a la brevedad.', category='success')
    else:
      flash('No hemos podido validar el mensaje. Complete correctamente los campos del formulario.', category='error')

  if origin == 'detail':
    return redirect(url_for('detail', id=int(id)))
  else:
    return redirect(url_for('home'))

@app.route('/vehicles_abm')
@login_required
def vehicles_abm():
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY domain ASC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('vehicles_abm.html', categories = importedCategories, vehicles = importedVehicles)

@app.route('/vhc_create')
@login_required
def vhc_create():
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY domain ASC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('vhc_create.html', categories = importedCategories, vehicles = importedVehicles)

@app.route('/vhc_save', methods = ["POST"])
@login_required
def vhc_save():

  cur = dbconnection.connection.cursor()

  domain = request.form['domain'].upper()
  #Validación del dominio
  sqlSentence = "SELECT COUNT(domain) FROM vehicle WHERE domain = '" + str(domain) + "'"
  cur.execute(sqlSentence)
  matchingDomain = cur.fetchone()[0]
  if matchingDomain:
      flash('El dominio ' + domain + ' ya existe en la base de datos. Puede volver y crear un vehículo con un dominio diferente o editar el existente a continuación:', category='error')
      sqlSentence = "SELECT * FROM vehicle WHERE domain = '" + str(domain) + "'"
      cur.execute(sqlSentence)
      matchingVehicle = cur.fetchall()[0]
      id = str(matchingVehicle[0])
      return redirect('/vhc_edit/' + id)

  title = request.form['title']
  brand= request.form['brand']
  model = request.form['model']
  year = int(request.form['year'])
  short_desc = request.form['short_desc']
  long_desc = request.form['long_desc']
  category = request.form['category']

  if request.form.get('promoted'):
    promoted = 1
  else:
    promoted = 0

  if request.form.get('visible'):
    visible = 1
  else:
    visible = 0

  image_00 = request.files['image_00']
  image_01 = request.files['image_01']
  image_02 = request.files['image_02']
  image_03 = request.files['image_03']
  image_04 = request.files['image_04']
  image_05 = request.files['image_05']
  image_06 = request.files['image_06']
  image_07 = request.files['image_07']
  image_08 = request.files['image_08']
  image_09 = request.files['image_09']

  if image_00.filename != '':
    image_00.filename = rename(image_00.filename)
    save_image(image_00)
  if image_01.filename != '':
    image_01.filename = rename(image_01.filename)
    save_image(image_01)
  if image_02.filename != '':
    image_02.filename = rename(image_02.filename)
    save_image(image_02)
  if image_03.filename != '':
    image_03.filename = rename(image_03.filename)
    save_image(image_03)
  if image_04.filename != '':
    image_04.filename = rename(image_04.filename)
    save_image(image_04)
  if image_05.filename != '':
    image_05.filename = rename(image_05.filename)
    save_image(image_05)
  if image_06.filename != '':
    image_06.filename = rename(image_06.filename)
    save_image(image_06)
  if image_07.filename != '':
    image_07.filename = rename(image_07.filename)
    save_image(image_07)
  if image_08.filename != '':
    image_08.filename = rename(image_08.filename)
    save_image(image_08)
  if image_09.filename != '':
    image_09.filename = rename(image_09.filename)
    save_image(image_09)

  rowData = (domain, image_00.filename, title, brand, model, year, short_desc, long_desc, category, promoted, visible, image_01.filename, image_02.filename, image_03.filename, image_04.filename, image_05.filename, image_06.filename, image_07.filename, image_08.filename, image_09.filename)

  cur.execute('SELECT COUNT(*) FROM vehicle')
  prev_rownumber = cur.fetchone()[0]

  sqlSentence = "INSERT INTO vehicle (id, domain, image_00, title, brand, model, year, short_desc, long_desc, category, promoted, visible, image_01, image_02, image_03, image_04, image_05, image_06, image_07, image_08, image_09) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  cur.execute(sqlSentence, rowData)
  dbconnection.connection.commit()

  cur.execute('SELECT COUNT(*) FROM vehicle')
  post_rownumber = cur.fetchone()[0]

  if post_rownumber == prev_rownumber:
    flash('No hemos podido cargar el vehículo en la base de datos. Por favor intente de nuevo en unos minutos.', category='error')
  else:
    flash('¡Vehículo almacenado correctamente! Puede seguir agregando o volver al listado de vehículos.', category='success')
  return redirect('/vhc_create')

@app.route('/vhc_delete/<int:id>')
@login_required
def vhc_delete(id):

  cur = dbconnection.connection.cursor()
  sqlSentence = "SELECT * FROM vehicle WHERE id = " + str(id)
  cur.execute(sqlSentence)
  matchingVehicles = cur.fetchall()
  selectedVehicle = matchingVehicles[0]

  if selectedVehicle[2] != '':
    remove_old_image('image_00', selectedVehicle[0], 'vehicle')

  for image_number in range(9):
    if selectedVehicle[image_number + 12] != '':
      image_column = 'image_0' + str(image_number + 1)
      remove_old_image(image_column, selectedVehicle[0], 'vehicle')

  cur = dbconnection.connection.cursor()

  cur.execute('SELECT COUNT(*) FROM vehicle')
  prev_rownumber = cur.fetchone()[0]

  sqlSentence = 'DELETE FROM vehicle WHERE id = ' + str(id)
  cur.execute(sqlSentence)
  dbconnection.connection.commit()

  cur.execute('SELECT COUNT(*) FROM vehicle')
  post_rownumber = cur.fetchone()[0]

  if post_rownumber == prev_rownumber:
    flash('No hemos podido eliminar el vehículo de la base de datos. Por favor intente de nuevo en unos minutos.', category='error')
  else:
    flash('¡Vehículo eliminado correctamente!', category='success')

  return redirect('../vehicles_abm')

@app.route('/vhc_edit/<int:id>')
@login_required
def vhc_edit(id):

  cur = dbconnection.connection.cursor()
  sqlSentence = "SELECT * FROM vehicle WHERE id = " + str(id)
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()
  selectedVehicle = importedVehicles[0]

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('vhc_edit.html', categories = importedCategories, vehicle = selectedVehicle)

@app.route('/vhc_update', methods = ["POST"])
@login_required
def vhc_update():

  cur = dbconnection.connection.cursor()

  id = request.form['id']
  domain = request.form['domain'].upper()

  sqlSentence = 'SELECT * FROM vehicle WHERE id = ' + str(id)
  cur.execute(sqlSentence)
  matchingVehicles = cur.fetchall()
  selectedVehicle = matchingVehicles[0]

  title = request.form['title']
  brand= request.form['brand']
  model = request.form['model']
  year = int(request.form['year'])
  short_desc = request.form['short_desc']
  long_desc = request.form['long_desc']
  category = request.form['category']

  if request.form.get('promoted'):
    promoted = 1
  else:
    promoted = 0

  if request.form.get('visible'):
    visible = 1
  else:
    visible = 0

  image_00 = request.files['image_00']
  image_01 = request.files['image_01']
  image_02 = request.files['image_02']
  image_03 = request.files['image_03']
  image_04 = request.files['image_04']
  image_05 = request.files['image_05']
  image_06 = request.files['image_06']
  image_07 = request.files['image_07']
  image_08 = request.files['image_08']
  image_09 = request.files['image_09']

  if image_00.filename != '':
    image_00.filename = rename(image_00.filename)
    if selectedVehicle[2] != '':
      remove_old_image('image_00', id, "vehicle")
    save_image(image_00)
    sqlSentence = "UPDATE vehicle SET image_00 = '" + image_00.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_01.filename != '':
    image_01.filename = rename(image_01.filename)
    if selectedVehicle[12] != '':
      remove_old_image('image_01', id, "vehicle")
    save_image(image_01)
    sqlSentence = "UPDATE vehicle SET image_01 = '" + image_01.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_02.filename != '':
    image_02.filename = rename(image_02.filename)
    if selectedVehicle[13] != '':
      remove_old_image('image_02', id, "vehicle")
    save_image(image_02)
    sqlSentence = "UPDATE vehicle SET image_02 = '" + image_02.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_03.filename != '':
    image_03.filename = rename(image_03.filename)
    if selectedVehicle[14] != '':
      remove_old_image('image_03', id, "vehicle")
    save_image(image_03)
    sqlSentence = "UPDATE vehicle SET image_03 = '" + image_03.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_04.filename != '':
    image_04.filename = rename(image_04.filename)
    if selectedVehicle[15] != '':
      remove_old_image('image_04', id, "vehicle")
    save_image(image_04)
    sqlSentence = "UPDATE vehicle SET image_04 = '" + image_04.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_05.filename != '':
    image_05.filename = rename(image_05.filename)
    if selectedVehicle[16] != '':
      remove_old_image('image_05', id, "vehicle")
    save_image(image_05)
    sqlSentence = "UPDATE vehicle SET image_05 = '" + image_05.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_06.filename != '':
    image_06.filename = rename(image_06.filename)
    if selectedVehicle[17] != '':
      remove_old_image('image_06', id, "vehicle")
    save_image(image_06)
    sqlSentence = "UPDATE vehicle SET image_06 = '" + image_06.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_07.filename != '':
    image_07.filename = rename(image_07.filename)
    if selectedVehicle[18] != '':
      remove_old_image('image_07', id, "vehicle")
    save_image(image_07)
    sqlSentence = "UPDATE vehicle SET image_07 = '" + image_07.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_08.filename != '':
    image_08.filename = rename(image_08.filename)
    if selectedVehicle[19] != '':
      remove_old_image('image_08', id, "vehicle")
    save_image(image_08)
    sqlSentence = "UPDATE vehicle SET image_08 = '" + image_08.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()
  if image_09.filename != '':
    image_09.filename = rename(image_09.filename)
    if selectedVehicle[20] != '':
      remove_old_image('image_09', id, "vehicle")
    save_image(image_09)
    sqlSentence = "UPDATE vehicle SET image_09 = '" + image_09.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()

  rowData = (id, domain, title, brand, model, year, short_desc, long_desc, category, promoted, visible, id)

  sqlSentence = "UPDATE vehicle SET id = %s, domain = %s, title = %s, brand = %s, model = %s, year = %s, short_desc = %s, long_desc = %s, category = %s, promoted = %s, visible = %s WHERE id = %s"
  cur.execute(sqlSentence, rowData)
  dbconnection.connection.commit()
  flash('¡La información del vehículo se ha actualizado correctamente!', category='success')

  return redirect('../vehicles_abm')

@app.route('/cat_create')
@login_required
def cat_create():
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY domain ASC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  return render_template('cat_create.html', categories = importedCategories, vehicles = importedVehicles)

@app.route('/cat_save', methods = ["POST"])
@login_required
def cat_save():

  name = request.form['name']

  if request.form.get('carousel'):
    carousel = 1
  else:
    carousel = 0
  image = request.files['image']
  if image.filename != '':
    image.filename = rename(image.filename)
    save_image(image)

  rowData = (name, image.filename, carousel)

  cur = dbconnection.connection.cursor()
  cur.execute('SELECT COUNT(*) FROM category')
  prev_rownumber = cur.fetchone()[0]

  sqlSentence = "INSERT INTO category (id, name, image, carousel) VALUES (NULL, %s, %s, %s)"
  cur.execute(sqlSentence, rowData)
  dbconnection.connection.commit()

  cur.execute('SELECT COUNT(*) FROM category')
  post_rownumber = cur.fetchone()[0]

  if post_rownumber == prev_rownumber:
    flash('No hemos cargar la categoría en la base de datos. Por favor intente de nuevo en unos minutos.', category='error')
  else:
    flash('¡Categoría almacenada correctamente! Puede seguir agregando o volver al listado de vehículos.', category='success')

  return redirect('/vehicles_abm')

@app.route('/cat_delete/<int:id>')
@login_required
def cat_delete(id):

  cur = dbconnection.connection.cursor()
  sqlSentence = "SELECT * FROM category WHERE id = " + str(id)
  cur.execute(sqlSentence)
  matchingVehicles = cur.fetchall()
  selectedVehicle = matchingVehicles[0]

  if selectedVehicle[2] != '':
    remove_old_image('image', selectedVehicle[0], 'category')

  cur.execute('SELECT COUNT(*) FROM category')
  prev_rownumber = cur.fetchone()[0]

  cur = dbconnection.connection.cursor()
  sqlSentence = 'DELETE FROM category WHERE id = ' + str(id)
  cur.execute(sqlSentence)
  dbconnection.connection.commit()

  cur.execute('SELECT COUNT(*) FROM category')
  post_rownumber = cur.fetchone()[0]

  if post_rownumber == prev_rownumber:
    flash('No hemos podido eliminar la categoría de la base de datos. Por favor intente de nuevo en unos minutos.', category='error')
  else:
    flash('¡Categoría eliminada correctamente!', category='success')

  return redirect('../vehicles_abm')

@app.route('/cat_edit/<int:id>')
@login_required
def cat_edit(id):
  cur = dbconnection.connection.cursor()

  sqlSentence = "SELECT * FROM vehicle ORDER BY id DESC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()

  sqlSentence = "SELECT * FROM category"
  cur.execute(sqlSentence)
  importedCategories = cur.fetchall()

  sqlSentence = "SELECT * FROM category WHERE id = " + str(id)
  cur.execute(sqlSentence)
  selectCategories = cur.fetchall()
  selectedCategory = selectCategories[0]

  return render_template('cat_edit.html', category = selectedCategory, categories = importedCategories, vehicles = importedVehicles)

@app.route('/cat_update', methods = ["POST"])
@login_required
def cat_update():

  cur = dbconnection.connection.cursor()

  id = request.form['id']
  name = request.form['name']
  if request.form.get('carousel'):
    carousel = 1
  else:
    carousel = 0
  image = request.files['image']
  if image.filename != '':
    image.filename = rename(image.filename)
    remove_old_image('image', id, "category")
    save_image(image)
    sqlSentence = "UPDATE category SET image = '" + image.filename + "' WHERE id = " + str(id)
    print(sqlSentence)
    cur.execute(sqlSentence)
    dbconnection.connection.commit()

  sqlSentence = "SELECT name FROM category WHERE id = " + str(id)
  cur.execute(sqlSentence)
  previousData = cur.fetchall()
  previousName = previousData[0][0]

  sqlSentence = "SELECT * FROM vehicle ORDER BY id DESC"
  cur.execute(sqlSentence)
  importedVehicles = cur.fetchall()
  for vehicle in importedVehicles:
    if vehicle[9] == previousName:
      rowData = (name, vehicle[0])
      sqlSentence = "UPDATE vehicle SET category = %s WHERE id = %s"
      cur.execute(sqlSentence, rowData)
      dbconnection.connection.commit()

  rowData = (name, carousel, id)
  sqlSentence = "UPDATE category SET name = %s, carousel = %s WHERE id = %s"
  cur.execute(sqlSentence, rowData)
  dbconnection.connection.commit()
  flash('¡Los datos de la categoría se han actualizado correctamente!', category='success')

  return redirect('../vehicles_abm')

def rename(oldname):
  oldname = oldname.replace(' ', '_')
  oldname = oldname.replace('(', '_')
  oldname = oldname.replace(')', '_')
  now = datetime.now()
  time = now.strftime('%Y%H%M%S')
  newname = time + "_" + oldname
  return newname

def save_image(image):
  image.save('./mysite/static/images/upload/' + image.filename)
  print('Saved!')

def remove_old_image(image_number, id, from_table):
  cur = dbconnection.connection.cursor()
  if from_table == "vehicle":
    sqlSentence = "SELECT " + image_number + " FROM vehicle WHERE id = " + str(id)
  else:
    sqlSentence = "SELECT image FROM category WHERE id = " + str(id)
  cur.execute(sqlSentence)
  rowSelected = cur.fetchall()
  fileToBeRemoved = os.path.join(app.config['FOLDER'], rowSelected[0][0])
  if os.path.exists(fileToBeRemoved):
    os.remove(fileToBeRemoved)
    print('Removed!')


@app.route('/log')
def log():
  return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    print(request.form['username'])
    print(request.form['password'])
    user = User(0,request.form['username'], request.form['password'])
    logged_user = ModelUser.login(dbconnection, user)
    if logged_user != None:
      if logged_user.password:
        login_user(logged_user)
        return redirect(url_for('vehicles_abm'))
      else:
        flash('Contraseña incorrecta')
        return render_template('auth/login.html')
    else:
      flash('No existe el usuario')
      return render_template('auth/login.html')
  else:
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
  logout_user()
  return redirect('/')

def status_401(error):
  return redirect(url_for('login'))

def status_404(error):
  return "<h1>Página no encontrada</h1>", 404


#----------------START-----------------


if __name__ == '__main__':
  app.config.from_object(config['development'])
  csrf.init_app(app)
  app.register_error_handler(401, status_401)
  app.register_error_handler(404, status_404)
  app.run()
