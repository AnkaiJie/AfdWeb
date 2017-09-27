from flask import Flask, request, render_template
from celery import Celery
from config import APP_NAME
from tasks import run_overcite_script, store_request
from datapython.apilib import ScopusApiLib
import pprint

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
        author_info = runner.getAuthorMetrics(form['author_id'])
        indexed_name = author_info['indexed-name']

        req_ip = request.environ.get('REMOTE_ADDR', '')
        req_raw = pprint.pformat(request.environ, depth=2)
        store_request.delay(form['author_id'], int(form['paper_num']),
            int(form['cite_num']), form['name'], form['email'], indexed_name, req_ip, req_raw)

        run_overcite_script.delay(form['author_id'], int(form['paper_num']),
            int(form['cite_num']), form['name'], form['email'], indexed_name)

        return render_template('finish.html') 
    except KeyError:
        return render_template('error.html') 
    
if __name__ == '__main__':
    app.run(debug=True)
