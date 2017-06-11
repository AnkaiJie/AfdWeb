## To run locally
0. Use Python 3
1. Go into project directory
2. Install the required python libraries either globally or on a python virtualenv - celery[redis], flask, pymysql, pandas, numpy, and requests
3. Start up celery with the command "celery -A .tasks worker -l info --concurrency=10" , or use any other viable configuration variable
4. Run "python app.py" to start on localhost
