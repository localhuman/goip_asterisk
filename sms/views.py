from django.shortcuts import render
from django.http.response import HttpResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404
# Create your views here.

from sms.models import SIPTerminus,SMSOut
from sms.tasks import notify_sms_sent_status

import os
import phonenumbers
import json
import uuid
import logging
import threading

logger = logging.getLogger(__name__)

def home(request):
    return HttpResponse('asterisk sms gateway?')

def send_sms(request):

    logger.debug('send sms call: %s ' % request.GET)

    #generate uuid for operational uses
    guid=uuid.uuid1()

    #create a database entry for this message
    sms = SMSOut(uuid=guid)
    sms.save()

    origin=None
    toAddr=None
    toRegion=None
    fromAddr=None
    fromSip=None
    message=None

    #first validate that all required fields are present
    errors=[]

    if 'origin' in request.GET:
        origin=request.GET.get('origin')
        sms.origin=origin
    else:
        errors.append('No Origin Specified')

    if 'message' in request.GET:
        message=request.GET.get('message')
        sms.text=message
    else:
        errors.append('No Message Specified')

    if 'to' in request.GET:
        toAddr=request.GET.get('to')
        sms.toNumber=toAddr
    else:
        errors.append('To Number not Specified')

    if 'to_region' in request.GET:
        toRegion=request.GET.get('to_region').upper()
    else:
        errors.append('No ISO to region Specified')

    if 'from' in request.GET:
        fromAddr=request.GET.get('from')
    else:
        errors.append('No From number Specified')

    if 'sip_address' in request.GET:
        fromSip = request.GET.get('sip_address')
    else:
        errors.append('No From SIP Address specified')

    sms.save()

    #return error message if missing required fields
    if len(errors):
        errorString = ','.join(errors)
        sms.status='FAILURE'
        sms.failure_reason=errorString
        sms.save()
        response = {'status':'Error', 'error':errorString}
        logger.debug('Incomplete request, returning errors: %s ' % response)
        return HttpResponseBadRequest(json.dumps(response),mimetype='application/json')

    #ok now  we check the phone number to see if it is valid for the region specified
    phone=None
    fromTerminus=None
    phoneError=None
    try:
        phone=phonenumbers.parse(toAddr,toRegion)
        if not phonenumbers.is_possible_number(phone):
            phoneError='Phone number %s not possible for region %s ' % (toAddr,toRegion)
        elif not phonenumbers.is_valid_number(phone):
            phoneError='Phone number %s not valid for region %s' % (toAddr,toRegion)

    except phonenumbers.NumberParseException as e:
        phoneError=str(e)

    #now make sure that the from number exists in database

    try:
        fromTerminus=SIPTerminus.objects.get(number=fromAddr)
        sms.fromNumber=fromTerminus
        sms.save()
    except SIPTerminus.DoesNotExist:
        phoneError='SIP Terminal with number %s not found' % fromAddr

    #if errors with the phone, return phone errors
    if phoneError:
        sms.status='FAILURE'
        sms.failure_reason=phoneError
        sms.save()
        response={'status':'Error','errors':phoneError}
        return HttpResponseBadRequest(json.dumps(response),mimetype='application/json')

    #ok looks like phone number is good, let's checking it
    sms.toNumber=phonenumbers.format_number(phone,phonenumbers.PhoneNumberFormat.E164)

    #now create the sms call file
    filename = 'sms-%s.call' % guid
    f = open('/tmp/%s' % filename,'w')
    f.write('Channel: %s\n' % fromTerminus.outboundSMSChannel)
    f.write('MaxRetries: 2\n')
    f.write('RetryTime: 60\n')
    f.write('WaitTime: 30\n')
    f.write('Context: %s\n' % fromTerminus.outboundSMSContext)
    f.write('Extension: %s\n' % fromTerminus.outboundSMSExtension)
    f.write('Setvar: SMSPK=%s\n' % sms.pk)
    f.write('Setvar: SMSOUT=%s\n' % sms.toAsteriskString)
    f.close()

    #file is created in the tmp directory
    #after creating it, now copy to the /var/spool/asterisk/outgoing/ directory
    #once this has been done, asterisk will initiate the sms#
    try:
        dest = '/var/spool/asterisk/outgoing/%s' % filename
        os.rename(f.name, dest)
    except OSError as e:
        errorString='An internal exception occurred while processing your response: %s. ' \
                    ' Please contact tasaunders@gmail.com if this problem persists.' % str(e)
        sms.status='FAILURE'
        sms.failure_reason=errorString
        sms.save()
        response = {'status':'Error','error':errorString}
        return HttpResponseBadRequest(json.dumps(response),mimetype='application/json')

    sms.status='QUEUED'
    sms.save()


    response={'status':'ok','aid':str(guid)}


    return HttpResponse(json.dumps(response),mimetype='application/json')

def update_sms_internal(request,sms_id):
    sms=None
    try:
        sms = SMSOut.objects.get(pk=sms_id)
    except SMSOut.DoesNotExist:
        error = 'Error: SMS with id: %s does not exist' % sms_id
        return HttpResponseBadRequest(error)

    status = request.GET.get('status')

    if status and len(status):
        sms.status=status
        sms.save()
        response = "SMS %s status updated to %s" % (sms_id,status)
        t = threading.Thread(target=notify_sms_sent_status, args=(sms,))
        t.start()
        return HttpResponse(response)

    response= "SMS %s status not updated" % sms_id
    return HttpResponse(response)
