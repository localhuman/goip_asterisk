from django.db import models
from django.db.models.signals import post_save
from sms.tasks import notify_sms_received


import threading
import urllib
# Create your models here.



class AppService(models.Model):
    title = models.CharField(max_length=64)
    sms_received_url=models.URLField()
    sms_received_method=models.CharField(max_length=4,choices={('GET','GET'),('POST','POST')})
    sms_sent_url = models.URLField()
    sms_sent_method = models.CharField(max_length=4,choices={('GET','GET'),('POST','POST')})

    def __unicode__(self):
        return self.title

class SIPTerminus(models.Model):
    name = models.CharField(max_length=32)
    number = models.CharField(max_length=16,unique=True)
    region = models.CharField(max_length=2)
    user = models.CharField(max_length=16)
    secret = models.CharField(max_length=16)
    host = models.CharField(max_length=64)
    app = models.ForeignKey(AppService)

    outboundSMSChannel=models.CharField(max_length=64)
    outboundSMSContext=models.CharField(max_length=64)
    outboundSMSExtension=models.CharField(max_length=64)

    outboundPhoneChannel=models.CharField(max_length=64)
    outboundPhoneContext=models.CharField(max_length=64)
    outboundPhoneExtension=models.CharField(max_length=64)

    @property
    def sipstring(self):
        return 'sip:%s@%s' % (self.user,self.host)

    def __unicode__(self):
        return '+%s' % self.number

class SMSIn(models.Model):

    text = models.CharField(max_length=512)
    fromNumber = models.CharField(max_length=16)
    toNumber = models.ForeignKey(SIPTerminus)
    uuid = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    app_response_code = models.CharField(max_length=3)
    app_response_text = models.CharField(max_length=256)

    def __unicode__(self):
        return "Inbound SMS %s " % self.text

class SMSOut(models.Model):
    text = models.CharField(max_length=512)
    fromNumber = models.ForeignKey(SIPTerminus,null=True)
    toNumber = models.CharField(max_length=16)
    uuid = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    origin = models.URLField()
    status=models.CharField(max_length=32,choices=[('RECEIVED','RECEIVED'),('QUEUED','QUEUED'),('SUCCESS','SUCCESS'),('FAILURE','FAILURE'),('INVALID_URI','INVALID_URI'),('INVALID_PROTOCOL','INVALID_PROTOCOL')], default='RECEIVED')
    failure_reason = models.CharField(max_length=1024, blank=True,null=True)

    app_response_code = models.CharField(max_length=3)
    app_response_text = models.CharField(max_length=256)

    @property
    def toAsteriskString(self):
        sms='%s\n%s' % (self.toNumber,self.text)
        encodedSMS = urllib.quote(sms,'')
        return encodedSMS

    def __unicode__(self):
        return "Outbound SMS: %s " % self.text




class InboundError(models.Model):
    inboud_sms=models.ForeignKey(SMSIn)
    app = models.ForeignKey(AppService)
    message = models.CharField(max_length=512)

    def __unicode__(self):
        return 'Url %s failed with message %s ' % (self.app.sms_received_url, self.message)


def sms_received(sender,instance,created,**kwargs):
    if created:
        t = threading.Thread(target=notify_sms_received,args=(instance,))
        t.start()

post_save.connect(sms_received, sender=SMSIn)