# Academic Fraud Detector

Mass data collection functions for publishers on Scopus API to determine suspects for citation fraud. Created as part of my Undergraduate Research Assistanceship at the University of Waterloo.

This repository examines the citing behaviours of academic authors, as determined through citation data as pulled from the Scopus academic database. To get further information on how it works, visit the live site at http://blizzard.cs.uwaterloo.ca/afdserver/ and click on "Need Help?"

## To run locally
0. Use Python 3
1. Go into project directory
2. Install the required python libraries either globally or on a python virtualenv - celery[redis], flask, pymysql, pandas, numpy, and requests
3. Start up celery with the command "celery -A .tasks worker -l info --concurrency=10" , or use any other viable configuration variable
4. Run "python app.py" to start on localhost
