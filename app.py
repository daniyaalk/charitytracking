from flask import Flask, request, session, render_template, redirect, url_for, flash, Response, send_from_directory
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators, IntegerField
import json
from datetime import datetime
import time

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

#To serve js files
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/', methods=['GET', 'POST'])
def home():

    if 'id' in session:
        return redirect(url_for('distributor'))
    else:

        if request.method == "POST":

            username = request.form['username']
            password = request.form['password']

            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM distributors WHERE username LIKE '"+ username +"' AND password='"+ password +"'")

            check = cur.fetchone()

            if bool(check):
                session['id'] = check['id']
                return redirect(url_for('distributor'))
            else:
                flash("Incorrect username or password", 'danger')
                return render_template('home.html')

        else:
            return render_template('home.html')

@app.route('/logout')
def logout():
    if 'admin' in session:
        session.pop('admin', None)

    if 'id' in session:
        session.pop('id', None)

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
            flash("Incorrect username or password", 'danger')
            return redirect(url_for('admin'))

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

@app.route('/distributor', methods=['GET','POST'])
def distributor():

    if 'id' not in session:
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as distr_count FROM distribution WHERE distributor_id='"+str(session['id'])+"'")

    return render_template('distributor.html', id=session['id'], count=cur.fetchone()['distr_count'])

class AddFamily(Form):
    name = StringField('Name', [validators.Length(max=100, min=1),validators.InputRequired()])

    plot_number = IntegerField('Plot Number', [validators.InputRequired()])
    gut_number = IntegerField('Gut Number', [validators.InputRequired()])
    occupation = StringField('Occupation', [validators.Length(max=50, min=1),validators.InputRequired()])
    layout = StringField('Layout', [validators.Length(max=50, min=1),validators.InputRequired()])
    mouza = StringField('Mouza', [validators.Length(max=50, min=1),validators.InputRequired()])

    mobile_number = IntegerField('Mobile Number', [validators.InputRequired(), validators.NumberRange(min=1000000000, max=9999999999, message="Enter a valid mobile number")])
    uuid = IntegerField('Aadhaar', [validators.InputRequired()])

    adults_count = IntegerField('Number of Adults', [validators.InputRequired()])
    children_count = IntegerField('Number of Children', [validators.InputRequired()])

@app.route('/add_family', methods=['GET', 'POST'])
def add_family():
    if 'id' not in session:
        return redirect(url_for('home'))
    else:

        form = AddFamily(request.form)

        if request.method=="POST" and form.validate():

            name = request.form['name']

            plot_number = request.form['plot_number']
            gut_number = request.form['gut_number']
            occupation = request.form['occupation']
            layout = request.form['layout']
            mouza = request.form['mouza']

            mobile_number = request.form['mobile_number']
            uuid = request.form['uuid']

            adults_count = request.form['adults_count']
            children_count = request.form['children_count']

            cur = mysql.connection.cursor()

            cur.execute("SELECT COUNT(*) AS family_check FROM families WHERE uuid='"+ uuid +"'")

            if(cur.fetchone()['family_check'])!=0:
                flash("Family already exists on record", 'warning')
                return redirect(url_for('add_family'))
            else:
                cur.execute("INSERT INTO `families` (`name`, `plot_number`, `gut_number`, `occupation`, `layout`, `mouza`, `mobile_number`, `uuid`, `adults_count`, `children_count`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, plot_number, gut_number, occupation, layout, mouza, mobile_number, uuid, adults_count, children_count))
                mysql.connection.commit()
                cur.close()

                flash("Successfully added", 'success')
                return redirect(url_for('add_family'))
        else:

            if request.method=="POST":
                flash("Please Fix the errors", 'warning')

            return render_template('add_family.html', form=form)

@app.route('/families')
def families():
    if 'id' not in session:
        return redirect(url_for('home'))
    else:

        return render_template('families.html')

#Family lookup API
@app.route('/api/family/<uuid>')
def get_family(uuid):
    if 'id' not in session:
        return null
    else:

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM families WHERE uuid='"+uuid+"'")
        data = cur.fetchone()

        if data:
            cur.execute("SELECT time FROM distribution WHERE family_uuid='"+uuid+"' ORDER BY time DESC")
            time_query=cur.fetchall()

            if time_query:
                data['time'] = datetime.utcfromtimestamp(time_query[0]['time']+19800).strftime('%d-%m-%Y')
            else:
                data['time'] = "Never"
        else:
            data=None

        return Response(json.dumps(data), mimetype='application/json')

@app.route('/add-distribution/<uuid>')
def distribute(uuid):
    if 'id' not in session:
        return null
    else:

        cur = mysql.connection.cursor()

        #INSERT INTO `distribution` (`id`, `distributor_id`, `family_uuid`, `time`) VALUES (NULL, '123', '123', '123');
        cur.execute("INSERT INTO `distribution` (`id`, `distributor_id`, `family_uuid`, `time`) VALUES (NULL, %s, %s, %s)",(str(session['id']), str(uuid), str(int(time.time()))))
        mysql.connection.commit()
        flash("The entry was successfully added!", "success")
        return redirect(url_for('families'))

app.run(debug=True);
