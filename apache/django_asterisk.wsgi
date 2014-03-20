__author__ = 'thomassaunders'

import os
import sys

path='/var/www/html/gsasterisk'

if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE']='asterisk.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()