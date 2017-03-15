from flask import Flask
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script

app = Flask(APP_NAME)

@app.route('/')
def index():
    return "Hello World!"


@app.route('/request/overcitesAuthor')
def send_overcites():
    print("print teets")
    result = run_overcite_script.delay("TEST")
    print(result)
    return "hello" 




app.run(debug=True)
