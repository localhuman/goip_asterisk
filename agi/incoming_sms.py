#!/usr/local/bin/python
import sys,os,datetime
import urllib
import uuid


def log(msg):
    open('/tmp/incomingsms.log','ab+').write("INCOMING SMS: %s: %s\n"%(datetime.datetime.now(),msg))

#setup django
#append asterisk django project

path='/var/www/html/gsasterisk'

if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE']='asterisk.settings'

log("trying to import django")

from django.db.models.loading import get_models

log("tried to import django")

loaded_models = get_models()

log("Tried to get models")

#import models
from sms.models import AppService,SIPTerminus,SMSIn

#default app service
service = AppService.objects.get(pk='532a5c8a680020046c330797')

log("ok, setup django")

AGIENV={}

env = ""
while(env != "\n"):

    env = sys.stdin.readline()
    envdata =  env.split(":")
    if len(envdata)==2:
        AGIENV[envdata[0].strip()]=envdata[1].strip()
    else:
        log('environmentdata %s  not 2 parts ' % envdata)


#create uuid for incoming message
uuid = uuid.uuid1()
#log("new uuid: %s " % uuid)


#sms comes in as uri encoded param as AGI arg 1
uri_encoded_sms = AGIENV['agi_arg_1']
decoded_message = urllib.unquote(uri_encoded_sms)
parts = decoded_message.split("\n")
phone = parts[0].replace("+","")
parts.pop(0)
message = "\n".join(parts)

log("RECEIVED MESSAGE %s from phone number %s " % (message,phone))

#get incoming sms user
user = AGIENV['agi_arg_2']
host = AGIENV['agi_arg_3']

log("user and host: %s %s " % (user,host))

try:
    terminus = SIPTerminus.objects.get(user=user,host=host)
    out='saving inbound message "%s" with terminus "%s" from "%s"\n' % (message,terminus,phone)
    log(out)
    try:
        smsin = SMSIn(text=message,fromNumber=phone,toNumber=terminus,uuid=uuid)
        smsin.save()
        out='saved sms in message %s ' % smsin.pk
        log(out)
    except Exception as e:
        log('exception: %s ' % str(e))

except SIPTerminus.DoesNotExist:
    log("sip terminus with user %s and host %s does not exist" % (user,host))

sys.exit()