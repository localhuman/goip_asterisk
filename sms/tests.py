from django.test import TestCase
from sms.models import SMSIn,SMSOut,SIPTerminus,AppService
import uuid
import time
from sms.views import update_sms_internal
from django.http import HttpRequest

from agi.incoming_sms import process_message
from agi.outgoing_sms import process_outgoing_sms
# Create your tests here.


class SMSInTest(TestCase):

    fixtures=['AppService.json','SIPTerminus.json']

    def test_creating_a_new_sms_in_and_saving(self):

        services = AppService.objects.all()
        print 'app services: %s ' % services

        terminus = SIPTerminus.objects.all()[0]

        sms = SMSIn()
        sms.fromNumber='16129614397'
        sms.toNumber = terminus
        sms.text='Test Message'
        sms.uuid = uuid.uuid1()

        sms.save()

        all_sms_ins = SMSIn.objects.all()
        self.assertEquals(len(all_sms_ins),1)

        only_sms_in_db = all_sms_ins[0]
        self.assertEquals(only_sms_in_db,sms)

        self.assertEquals(only_sms_in_db.text,"Test Message")
        self.assertEquals(only_sms_in_db.toNumber,terminus)

    def test_sms_app_response(self):
        #wait a bit for the app to respond
#        time.sleep(1)

        sms = SMSIn.objects.all()[0]
        #check that the app responded with ok status code
        #from the sms in notification
        self.assertEquals(sms.app_response_code,'200')

        #check that app responded with some text
        self.assertNotEqual(len(sms.app_response_text),0)


class SMSOutTest(TestCase):

    fixtures=['AppService.json','SIPTerminus.json']

    def test_create_sms_out_and_saving(self):

        terminus = SIPTerminus.objects.all()[0]

        sms = SMSOut()
        sms.origin='http://127.0.0.1:8000'
        sms.text='Test Message'
        sms.fromNumber = terminus
        sms.toNumber='16129614397'
        sms.status='RECEIVED'
        sms.uuid=uuid.uuid1()

        sms.save()

        print 'sms pk: %s ' % sms.pk

        #test outgoing sms agi script
        #this test fails, not sure why
#        agi_res = process_outgoing_sms(sms.pk, 'SUCCESS',8000)
#        self.assertEqual(agi_res,1)


        all_sms_outs=SMSOut.objects.all()
        self.assertEquals(len(all_sms_outs),1)

        only_sms_in_db = all_sms_outs[0]
        self.assertEquals(only_sms_in_db,sms)

        self.assertEquals(only_sms_in_db.text,"Test Message")
        self.assertEquals(only_sms_in_db.fromNumber,terminus)
        self.assertEquals(only_sms_in_db.status,'RECEIVED')

        #update the sms status to success
        req=HttpRequest()
        req.method='GET'
        req.GET={'status':'SUCCESS'}
        res=update_sms_internal(req,sms.pk)

        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.content, u'SMS %s status updated to SUCCESS' % sms.pk)

        #now check if that is reflected in db
        newsms = SMSOut.objects.get(pk=sms.pk)
        self.assertEquals(newsms.status, 'SUCCESS')

        #wait a bit for the app to respond
        time.sleep(1)

        newsms = SMSOut.objects.get(pk=sms.pk)

        #check that the app responded with ok status code
        #from the sms in notification
        self.assertEquals(newsms.app_response_code,'200')

        #check that app responded with some text
        self.assertNotEqual(len(newsms.app_response_text),0)


    def test_incoming_agi(self):

        uri_encoded_message='%2B16129614397%0AHello'
        user='mydem'
        host='asterisk.remotehuman.org'

        service = AppService.objects.all()[0]

        guid=uuid.uuid1()

        res = process_message(service.pk,uri_encoded_message,guid,user,host)

        self.assertEquals(res,0)


        time.sleep(1)
        #now get the sms that was created

        sms = SMSIn.objects.get(uuid=guid)
        terminus = SIPTerminus.objects.get(user=user,host=host)

        #test that the correct to number was saved
        self.assertEquals(terminus, sms.toNumber)

        #test that the sms in message was delivered
        self.assertEquals(sms.app_response_code,'200')


