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
from datapython.apilib import storeAuthorMain, storeRequestInfo
from datapython.analysis import Analysis
import traceback

capp = Celery(APP_NAME)
capp.config_from_object(CeleryConfig)
logger = get_task_logger(APP_NAME)

def send_email(subject, toaddr, msg, attach_path=None):
    fromaddr = "academic.influence.analyzer@gmail.com"
    fullEmail = MIMEMultipart()
    fullEmail['Subject'] = subject
    fullEmail['From'] = "academic.influence.analyzer@gmail.com"
    fullEmail['To'] = toaddr
    mimemsg = MIMEText(msg)
    fullEmail.attach(mimemsg)
    
    if attach_path:
        part = MIMEBase('application', 'octet-stream')
        filename = attach_path.split('/')[-1]
        attachment = open(attach_path, "rb")
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        fullEmail.attach(part)
        
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "Flash1273")
    text = fullEmail.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def send_email_success(author_id, name, email, zipath, author_name):
    msg = "Hello %s, analyzing %s with author id %s" % (name, author_name, author_id)    
    subject = "Analysis for author " + str(author_id)
    send_email(subject, email, msg, attach_path=zipath)

def send_email_failure(author_id, name, email, author_name, pnum, where):
    msg = """Hey %s, we were unable to analyze %s with author id %s 
    due to an internal error. We will investigate this error and contact you when it is 
    fixed. Thanks for your patience.""" % (name, author_name, author_id)
    subject = "Unable to analyze author: " + str(author_id)
    send_email(subject, email, msg)

    msg2 = """User with email %s has encountered an error while 
    investigating %s with author_id %s. Requested paper num was %d and 
    request cite num was %d. Error was thrown in %s. 
    Please investigate.""" % (email, author_name, author_id, pnum, where)
    subject2 = "Error thrown on academic influence analyzer."
    admin_recipient = 'ankaijie@gmail.com'
    send_email(subject2, admin_recipient, msg2)


def analyze(author_id, name, email, table_names, author_name):
    # least cited citing papers
    tool = Analysis(author_id, table_names)
    to_zip = tool.getChartNames()

    name_process = author_name.split()[0].lower().replace('.','').replace(',','').strip()
    zipath = 'datapython/graphs/' + author_id + '_' + name_process +  '_influencedata.zip'
    with ZipFile(zipath, 'w') as myzip:
        for path in to_zip:
            filename = path.split('/')[-1]
            myzip.write(path, filename)

    #send_email_success(author_id, name, email, zipath, author_name)


@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    # don't be a daemon, so we can create new subprocesses
    from multiprocessing import current_process
    current_process().daemon = False

@capp.task
def run_overcite_script(author_id, pnum, name, email, author_name):

    table_names = storeAuthorMain(author_id, start_index=0, pap_num=pnum, 
        workers=10, targetNum=200, test=False)
    print(table_names)

    if table_names is None:
        send_email_failure(author_id, name, email, author_name, pnum,
            where='apilib script')
        return

    try:
        analyze(author_id, name, email, table_names, author_name)
    except Exception:
        print(traceback.format_exc())
        send_email_failure(author_id, name, email, author_name, pnum,
            where='analyze script, with exception: ' + traceback.format_exc())

@capp.task
def store_request(author_id, pnum, name, email, author_name, req_ip, request_raw):
    storeRequestInfo(author_id, author_name, pnum, name, email, req_ip, request_raw)
