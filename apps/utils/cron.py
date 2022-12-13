import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from apps.models import Post


def my_scheduled_job():
    post = Post.objects.order_by('-created_at').first()
    post.title = 'cron change'
    post.save()
