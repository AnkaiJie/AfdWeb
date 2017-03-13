from __future__ import absolute_import
from celery import shared_task
import os
import sys
import django
import time

import smtplib
from email.mime.text import MIMEText


sys.path.append("/home/ankai/Development/AfdWeb")
os.environ["DJANGO_SETTINGS_MODULE"] = "AfdWeb.settings"
django.setup()


@shared_task
def test(param):
    return 'The test task executed with argument ' + str(param)


@shared_task
def send_result(author_id):

    fromaddr = "kingshruf8@gmail.com"
    toaddr = "ankaijie@gmail.com"
    msg = MIMEText("YOUR MESSAGE HERE " + author_id)
    msg['From'] = "kingshruf8@gmail.com"
    msg['To'] = "ankaijie@gmail.com"
    msg['Subject'] = "SUBJECT OF THE MAIL"

    for i in range(10):
        time.sleep(2)
        print(i)
     
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login(fromaddr, "Flash1273")
    # text = msg.as_string()
    # server.sendmail(fromaddr, toaddr, text)
    # server.quit()
