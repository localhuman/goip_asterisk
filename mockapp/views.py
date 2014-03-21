# Create your views here.

from django.http import HttpResponse
import json
import logging

logger = logging.getLogger('mockapp')


def home(request):

    return HttpResponse('mock app home')


def sms_received(request):

    params={}

    if request.POST:
        params = request.POST
    else:
        params = request.GET

    res = {'status':'ok','params':params}

    return HttpResponse(json.dumps(res),mimetype='application/json')

def sms_sent(request):

    params={}

    if request.POST:
        params = request.POST
    else:
        params = request.GET

    res = {'status':'ok','params':params}

    return HttpResponse(json.dumps(res),mimetype='application/json')
