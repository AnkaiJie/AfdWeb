from flask import Flask, request, render_template
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script
from datapython.apilib import ScopusApiLib

app = Flask(APP_NAME)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/request/overcitesAuthor', methods=['POST'])
def send_overcites():
    form = request.form
    runner = ScopusApiLib()
    # print(form['author_id'])
    try:
    	testAuthor = runner.getAuthorMetrics(form['author_id'])
    	result = run_overcite_script.delay(form['author_id'], form['name'], form['email'])
    	return render_template('finish.html') 
    except KeyError as e:
    	return render_template('error.html') 
    




app.run(debug=True)
