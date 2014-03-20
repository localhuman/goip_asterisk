#!/usr/local/bin/python

import sys,datetime
import requests

def log(msg):
    open('/tmp/smsout.log','ab+').write("OUTGOING SMS: %s: %s\n"%(datetime.datetime.now(),msg))

AGIENV={}

log('attempting to process outgoing sms')

try:
    env = ""
    while(env != "\n"):

        env = sys.stdin.readline()
        envdata =  env.split(":")
        if len(envdata)==2:
            AGIENV[envdata[0].strip()]=envdata[1].strip()
        else:
            log('environmentdata %s  not 2 parts ' % envdata)

    log(AGIENV)

    #get outgoing sms id
    smspk = AGIENV['agi_arg_1']

    #get outgoing sms status
    status = AGIENV['agi_arg_2']

    url='http://127.0.0.1/sms/%s/update/?status=%s' % (smspk,status)

    log('url to connect to is %s' % url)

    req = requests.get(url)

    output = 'Update SMS-- HTTP RESPONSE: %s MESSAGE: %s ' % (req.status_code, req.text)

    log('result: %s ' % output)

except Exception as e:
    log('exception processing outgoing sms: %s ' % str(e))

sys.exit()