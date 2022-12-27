from django.test import TestCase
from django.urls import reverse


class UrlTest(TestCase):

    def test_login_url(self):
        url = reverse('login')
        self.assertURLEqual(url, '/login')


    def test_register_url(self):
        url = reverse('register')
        self.assertURLEqual(url, '/register')


