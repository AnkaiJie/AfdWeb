from __future__ import absolute_import
from config import *
from celery import Celery, shared_task
from celery.utils.log import get_task_logger
from celery.signals import worker_process_init
import smtplib
from zipfile import ZipFile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datapython.apilib import storeAuthorMain
from datapython.analysis import Analysis
import time

capp = Celery(APP_NAME)
capp.config_from_object(CeleryConfig)
logger = get_task_logger(APP_NAME)

def send_email(author_id, name, email, zipath):
    fromaddr = "kingshruf8@gmail.com"
    toaddr = email
    msg = MIMEText("Hello " + name + ", analyzing " + author_id)
    msg['From'] = "kingshruf8@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Analysis for author " + author_id

    fullEmail = MIMEMultipart()
    filename = zipath.split('/')[2]
    attachment = open(zipath, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    fullEmail.attach(msg)
    fullEmail.attach(part)
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "Flash1273")
    text = fullEmail.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def analyze(author_id, name, email, table_names):
    tool = Analysis(author_id, table_names)
    barpath = tool.plotOvercitesBar(author_id)
    histpath = tool.plotOvercitesHist(author_id)
    csvpath = tool.overcitesCsv(author_id)
    zipath = 'datapython/graphs/' + author_id + '_overcitedata.zip'
    with ZipFile(zipath, 'w') as myzip:
        myzip.write(barpath)
        myzip.write(histpath)
        myzip.write(csvpath)

    send_email(author_id, name, email, zipath)

@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    # don't be a daemon, so we can create new subprocesses
    from multiprocessing import current_process
    current_process().daemon = False

@capp.task
def run_overcite_script(author_id, name, email):
    table_names = storeAuthorMain(author_id, start_index=0, pap_num=1, cite_num=1, workers=1)
    analyze(author_id, name, email, table_names)


