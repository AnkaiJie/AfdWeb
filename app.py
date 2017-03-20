from flask import Flask, request, render_template
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script

app = Flask(APP_NAME)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/request/overcitesAuthor', methods=['POST'])
def send_overcites():
    form = request.json
    # print(form['author_id'])
    result = run_overcite_script.delay(form['author_id'])
    return "hello" 




app.run(debug=True)
