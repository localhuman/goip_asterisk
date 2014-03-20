
import requests
import json
import urllib

import logging

logger = logging.getLogger('tasks')

def notify_sms_received(sms):

    logger.debug('notify sms received!')

    dest_url = sms.toNumber.app.sms_received_url
    dest_method = sms.toNumber.app.sms_received_method

    message=sms.text

    params = {'message':message,
              'sip_address':sms.toNumber.sipstring,
              'to':sms.toNumber.number,
              'from':sms.fromNumber,
              'aid':sms.uuid,
              'datatype':'json'
    }

    if dest_method=='POST':
        requests.post(dest_url, data= json.dumps(params))
    else:
        logger.debug('sms received trying get!')
        try:
            encoded_params = urllib.urlencode(params)
            full_url = '%s?%s' % (dest_url,encoded_params)
            result = requests.get(full_url)
            logger.debug('sms recevied sent with response %s %s ' % (result.status_code, result.text))
        except Exception as e:
            logger.debug('error retreiving url %s ' % str(e))


def notify_sms_sent_status(sms):

    dest_url = sms.fromNumber.app.sms_sent_url
    method = sms.fromNumber.app.sms_sent_method

    params = {
        'aid': sms.uuid,
        'from':sms.fromNumber.number,
        'to':sms.toNumber,
        'status':sms.status,
    }

    if method=='GET':
        encoded_params = urllib.urlencode(params)
        full_url = '%s?%s' % (dest_url,encoded_params)
        requests.get(full_url)
    else:
        requests.post(dest_url, data= json.dumps(params))

