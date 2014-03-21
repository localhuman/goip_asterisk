"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import LiveServerTestCase
from selenium import  webdriver
from selenium.webdriver.common.keys import Keys
import bson
import os
from django.core import management
from django.contrib.auth.models import User

class FFTest(LiveServerTestCase):


    fixtures=['AppService.json','SIPTerminus.json']

    def setUp(self):

        #we can't dump a user object with the dumpdata command
        #in django non-rel, so its hard to make fixtures for that
        #but we'll manually create one here
        user = User(username='localhuman',email='tasaunders@gmail.com',
                    password='pbkdf2_sha256$10000$a99d5yXnnAwH$fWiihHipmG51hhLcjApSuX8HYi35X5GeSz1sWGpw870=',
                    is_superuser=True,is_staff=True)
        user.save()


        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_poll_via_admin_site(self):

        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.live_server_url + '/admin/')

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # She types in her username and passwords and hits return
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('localhuman')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('900wolves')
        password_field.send_keys(Keys.RETURN)

        # her username and password are accepted, and she is taken to
        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        # TODO: use the admin site to create a Poll
#        self.fail('finish this test')

