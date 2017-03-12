from __future__ import absolute_import
from celery import shared_task
import os
import sys
import django

sys.path.append("/home/ankai/Development/AfdWeb")
os.environ["DJANGO_SETTINGS_MODULE"] = "AfdWeb.settings"
django.setup()


@shared_task
def test(param):
	return 'The test task executed with argument ' + str(param)
