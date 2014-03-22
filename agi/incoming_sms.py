#!/usr/local/bin/python

import sys,os
import uuid
import urllib
from agi import AGI
import datetime
import base64


def log(msg):
    open('/tmp/incomingsms.log','ab+').write("INCOMING SMS: %s: %s\n"%(datetime.datetime.now(),msg))


def process_message(app_pk, message_body, guid, user,host):

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
    service = AppService.objects.get(pk=app_pk)

    log("ok, setup django")

    parts = message_body.split("\n")
    phone = parts[0].replace("+","")
    parts.pop(0)
    message = "\n".join(parts)

    log("RECEIVED MESSAGE %s from phone number %s " % (message,phone))
    log("user and host: %s %s " % (user,host))

    try:
        terminus = SIPTerminus.objects.get(user=user,host=host)
        out='saving inbound message "%s" with terminus "%s" from "%s"\n' % (message,terminus,phone)
        log(out)
        try:
            smsin = SMSIn(text=message,fromNumber=phone,toNumber=terminus,uuid=guid)
            smsin.save()
            out='saved sms in message %s ' % smsin.pk
            log(out)
            return 0
        except Exception as e:
            log('exception: %s ' % str(e))

    except SIPTerminus.DoesNotExist:
        log("sip terminus with user %s and host %s does not exist" % (user,host))

    return 1


if __name__=='__main__':

    myagi = AGI()
    log('processing sms')
    b64String=myagi.env['agi_arg_1']
#    uri_encoded_sms = myagi.env['agi_arg_1']
#    user = myagi.env['agi_arg_2']
#    host = myagi.env['agi_arg_3']
    user='mydem'
    host='asterisk.remotehuman.org'
    app_pk='532a5c8a680020046c330797'

    log('b64string: %s ' % b64String)

    message_body=base64.decodestring(b64String)

    #create uuid for incoming message
    guid = uuid.uuid1()

    log("a, m, u, h: %s %s %s %s " %(app_pk,message_body,user,host))

    res = process_message(app_pk,message_body,guid, user,host)
    log('result of process message %s ' % res)
    sys.exit(res)