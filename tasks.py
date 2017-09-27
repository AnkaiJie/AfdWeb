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

def send_email_failure(author_id, name, email, author_name, pnum, cnum, where):
    msg = """Hey %s, we were unable to analyze %s with author id %s 
    due to an internal error. We will investigate this error and contact you when it is 
    fixed. Thanks for your patience.""" % (name, author_name, author_id)
    subject = "Unable to analyze author: " + str(author_id)
    send_email(subject, email, msg)

    msg2 = """User with email %s has encountered an error while 
    investigating %s with author_id %s. Requested paper num was %d and 
    request cite num was %d. Error was thrown in %s. 
    Please investigate.""" % (email, author_name, author_id, pnum, cnum, where)
    subject2 = "Error thrown on academic influence analyzer."
    admin_recipient = 'ankaijie@gmail.com'
    send_email(subject2, admin_recipient, msg2)


def analyze(author_id, name, email, table_names_bylast, table_names_byfront, author_name):
    to_zip = []
    # least cited citing papers
    tool = Analysis(author_id, table_names_bylast, citing_sort="lower_citing")
    barpath = tool.plotOvercitesBar(author_id)
    histpath = tool.plotOvercitesHist(author_id)
    csvpath = tool.overcitesCsv(author_id)
    to_zip += [barpath, histpath, csvpath]

    # most cited citing papers
    tool2 = Analysis(author_id, table_names_byfront, citing_sort="upper_citing")
    barpath2 = tool2.plotOvercitesBar(author_id)
    histpath2 = tool2.plotOvercitesHist(author_id)
    csvpath2 = tool2.overcitesCsv(author_id)
    to_zip += [barpath2, histpath2, csvpath2]

    to_zip += ['datapython/graphs/README.pdf']

    zipath = 'datapython/graphs/' + author_id + '_overcitedata.zip'
    with ZipFile(zipath, 'w') as myzip:
        for path in to_zip:
            myzip.write(path)

    send_email_success(author_id, name, email, zipath, author_name)

@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    # don't be a daemon, so we can create new subprocesses
    from multiprocessing import current_process
    current_process().daemon = False

@capp.task
def run_overcite_script(author_id, pnum, cnum, name, email, author_name):
    table_names_bylast = storeAuthorMain(author_id, start_index=0, pap_num=pnum, cite_num=cnum,
        citing_sort="citations_lower", workers=10)

    if table_names_bylast is None:
        send_email_failure(author_id, name, email, author_name, pnum,
            cnum, where='apilib script bylast')
        return

    table_names_byfront = storeAuthorMain(author_id, start_index=0, pap_num=pnum, cite_num=cnum,
        citing_sort="citations_upper", workers=10)

    if table_names_byfront is None:
        send_email_failure(author_id, name, email, author_name, pnum,
            cnum, where='apilib script byfront')
        return

    try:
        analyze(author_id, name, email, table_names_bylast, table_names_byfront, author_name)
    except Exception:
        send_email_failure(author_id, name, email, author_name, pnum, cnum,
            where='analyze script, with exception: ' + traceback.format_exc())

@capp.task
def store_request(author_id, pnum, cnum, name, email, author_name, req_ip, request_raw):
    storeRequestInfo(author_id, author_name, pnum, cnum, name, email, req_ip, request_raw)

