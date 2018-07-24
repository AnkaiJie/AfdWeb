import sys
import subprocess

activate_this = '/var/www/html/afdserver/afdenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/html/afdserver')
from app import app as application

# import tasks
# cel = 'celery -A .tasks worker -l info --concurrency=10'
# subprocess.call(cel.split())
