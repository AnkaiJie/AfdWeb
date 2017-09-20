from flask import Flask, request, render_template
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script
from datapython.apilib import ScopusApiLib

app = Flask(__name__) 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request/overcitesAuthor', methods=['POST'])
def send_overcites():
    form = request.form
    runner = ScopusApiLib()
    # print(form['author_id'])
    try:
        runner.getAuthorMetrics(form['author_id'])
        run_overcite_script.delay(form['author_id'], form['paper_num'],
            form['cite_num'], form['name'], form['email'])
        return render_template('finish.html') 
    except KeyError as e:
        return render_template('error.html') 
    



if __name__ == '__main__':
    app.run(debug=True)
