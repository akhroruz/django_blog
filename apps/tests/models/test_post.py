# ### test_views.py
# from django.test import TestCase
#
# from apps.models import Post
#
#
# class UserViewTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         number_of_students = 30
#         # for student_id in range(number_of_students):
#         #     Post.objects.create()
#
#     def test_url_exists(self):
#         response = self.client.get("/students")
#         self.assertEqual(response.status_code, 200)
#
#     def test_url_accessible_by_name(self):
#         response = self.client.get(reverse('students'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_view_uses_correct_template(self):
#         response = self.client.get(reverse('students'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'testing/student_list.html')
#
#     def test_pagination_is_correct(self):
#         response = self.client.get(reverse('students'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue('is_paginated' in response.context)
#         self.assertTrue(response.context['is_paginated'] is True)
#         self.assertEqual(len(response.context['student_list']), 10)
