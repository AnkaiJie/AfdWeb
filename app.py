from flask import Flask, request
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script

app = Flask(APP_NAME)

@app.route('/')
def index():
    return "Hello World!"


@app.route('/request/overcitesAuthor')
def send_overcites(request):
    form = request.form
    print(form['author_id'])
    # result = run_overcite_script.delay("TEST")
    return "hello" 




app.run(debug=True)
