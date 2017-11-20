from flask import Flask, request, render_template, session, redirect, g, url_for
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script, store_request
from datapython.apilib import ScopusApiLib
from datapython.credentials import LOGINUSER, LOGINPASS
import pprint
import os

app = Flask(__name__)
app.secret_key = os.urandom(20)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        if request.form['username'].lower() == LOGINUSER and request.form['password'] == LOGINPASS:
            session['user'] = request.form['username']
            return redirect('/index')
        else:
            return render_template('login.html', passStatus='Incorrect Login')
    return render_template('login.html')


@app.route('/index')
def index():
    if g.user:
        return render_template('index.html')

    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user= None
    if 'user' in session:
        g.user = session['user']


@app.route('/request/overcitesAuthor', methods=['POST'])
def send_overcites():
    form = request.form
    runner = ScopusApiLib()
    # print(form['author_id'])
    try:
        author_info = runner.getAuthorMetrics(form['author_id'])
        indexed_name = author_info['indexed-name']

        req_ip = request.environ.get('REMOTE_ADDR', '')
        req_raw = pprint.pformat(request.environ, depth=2)

        store_request.delay(form['author_id'], int(form['paper_num']),
            form['name'], form['email'], indexed_name, req_ip, req_raw)

        run_overcite_script.delay(form['author_id'], int(form['paper_num']),
            form['name'], form['email'], indexed_name)

        return render_template('finish.html')
    except KeyError:
        return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
