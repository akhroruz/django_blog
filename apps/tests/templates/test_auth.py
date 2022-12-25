# from django.test import TestCase
# from django.urls import reverse
#
# from apps.models import Post
#
#
# class TemplateTest(TestCase):
#
#     def test_index_templates(self):
#         url = reverse('index')
#
#         response = self.client.get(url)
#         # self.assertContains(response.context, 'posts')
#         posts = Post.active.all()[:4]
#         self.assertEqual(response.context['posts'], posts)
#         self.assertTemplateUsed(response, 'apps/index.html')
#
#
