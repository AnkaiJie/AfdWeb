from __future__ import absolute_import
from config import *
from celery import Celery, shared_task
from celery.utils.log import get_task_logger
import smtplib
from email.mime.text import MIMEText


import time

capp = Celery(APP_NAME)
capp.config_from_object(CeleryConfig)
logger = get_task_logger(APP_NAME)

@shared_task
def run_overcite_script(author_id):
    fromaddr = "kingshruf8@gmail.com"
    toaddr = "ankaijie@gmail.com"
    msg = MIMEText("YOUR MESSAGE HERE " + author_id)
    msg['From'] = "kingshruf8@gmail.com"
    msg['To'] = "ankaijie@gmail.com"
    msg['Subject'] = "SUBJECT OF THE MAIL"

    for i in range(10):
        time.sleep(2)
        print(i)
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "Flash1273")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


    return "FiNISHED"

