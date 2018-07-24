import sys
import subprocess

activate_this = '/home/ankaijie/afdserver/afdenv2/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

cel = 'celery -A .tasks worker -l info --concurrency=10'
subprocess.call(cel.split())

sys.path.insert(0, '/home/ankaijie/afdserver/app.py')

