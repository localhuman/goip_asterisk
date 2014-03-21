#!/usr/local/bin/python

import sys,datetime
import requests

from agi import AGI

def log(msg):
    open('/tmp/smsout.log','ab+').write("OUTGOING SMS: %s: %s\n"%(datetime.datetime.now(),msg))


def process_outgoing_sms(smspk,status,port=80):

    url='http://127.0.0.1:%s/sms/%s/update/?status=%s' % (port,smspk,status)
    print 'url: %s ' % url
    log('url to connect to is %s' % url)

    req = requests.get(url)

    output = 'Update SMS-- HTTP RESPONSE: %s MESSAGE: %s ' % (req.status_code, req.text)

    log('result: %s ' % output)

    if req.status_code==200:
        return 0
    return req.text

if __name__=='__main__':

    log('attempting to process outgoing sms')

    agi = AGI()

    smspk = agi.env['agi_arg_1']
    status = agi.env['agi_arg_2']

    res = process_outgoing_sms(smspk,status,80)

    sys.exit(res)

