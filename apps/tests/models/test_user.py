from django.test import TestCase

from apps.models import User


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='username1', email='user1@mail.ru', password='user1')
        user2 = User.objects.create_user(username='username2', email='user2@mail.ru', password='user2')

    def test_create_user(self):
        user1 = User.objects.get(username='username1')
        count = User.objects.count()
        self.assertEqual(count, 2)
        self.assertFalse(user1.is_active)

    def test_create_super_user(self):
        count_1 = User.objects.filter(is_superuser=True).count()

        admin1 = User.objects.create_superuser(username='admin1', email='admin1@mail.ru', password='admin1')
        admin2 = User.objects.create_superuser(username='admin2', email='admin2@mail.ru', password='admin2')

        count_2 = User.objects.filter(is_superuser=True).count()
        self.assertEqual(count_2 - count_1, 2)
        self.assertTrue(admin1.is_active)

    #
    # def test_url_exists(self):
    #     response = self.client.get("/students")
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_url_accessible_by_name(self):
    #     response = self.client.get(reverse('students'))
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_view_uses_correct_template(self):
    #     response = self.client.get(reverse('students'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'testing/student_list.html')
    #
    # def test_pagination_is_correct(self):
    #     response = self.client.get(reverse('students'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue('is_paginated' in response.context)
    #     self.assertTrue(response.context['is_paginated'] is True)
    #     self.assertEqual(len(response.context['student_list']), 10)
