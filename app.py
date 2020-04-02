from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators, IntegerField

app = Flask(__name__)
app.secret_key = 'JFBSBFWMDSLKHHDKME'

#MySQL Credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'charity'
app.config['MYSQL_PASSWORD'] = '1qaz2wsx'
app.config['MYSQL_DB'] = 'charity'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MySQL
mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/logout')
def logout():
    if 'admin' in session:
        session.pop('admin', None)

    if 'username' in session:
        session.pop('username', None)

    return redirect("/")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        if 'admin' in session:
            return render_template('admin.html')
        else:
            return render_template('admin_login.html')
    else:
        if request.form['username'] == 'admin' and request.form['password'] == '1qaz2wsx':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "nay"

@app.route('/distributors')
def distributors():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    else:

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM distributors")
        dist_list = cur.fetchall()
        #print(dist_list)

        return render_template('distributors.html', list=dist_list)


#Add distributors form class
class AddDistributor(Form):

    username = StringField('Username', [validators.Length(max=50, min=1),validators.InputRequired()])
    password = StringField('Password', [validators.Length(max=50, min=1),validators.InputRequired()])
    service_point = StringField('Service Point', [validators.Length(max=100, min=1),validators.InputRequired()])
    gut_number = IntegerField('Gut Number', [validators.InputRequired()])

@app.route('/add_distributor', methods=['GET','POST'])
def add_distributor():

    if 'admin' not in session:
        return redirect(url_for('admin'))

    form = AddDistributor(request.form)

    if request.method == "POST" and form.validate():

        username = request.form['username']
        password = request.form['password']
        service_point = request.form['service_point']
        gut_number = request.form['gut_number']

        cur = mysql.connection.cursor()
        #print("INSERT INTO distributors VALUES('', '%s', '%s', '%s', '%s')", (username, password, service_point, gut_number))

        cur.execute("SELECT COUNT(*) AS username_check FROM distributors WHERE username='"+ username +"'")
        check = cur.fetchone()


        if check['username_check'] == 0:

            cur.execute("INSERT INTO distributors VALUES(NULL, '"+ username +"', '"+ password +"', '"+ service_point +"', '"+ gut_number +"' )")

            mysql.connection.commit()
            cur.close()

            flash("User has been registered", 'success')
            return redirect(url_for('distributors'))

        else:

            flash("That user already exists", 'warning')
            return redirect(url_for('distributors'))


    return render_template('add_distributor.html', form=form)

app.run(debug=True);
