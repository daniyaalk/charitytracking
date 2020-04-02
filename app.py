from flask import Flask, request, session, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        if 'admin' in session:
            return 'admin'
        else:
            return render_template('home.html')

app.run(debug=True);
