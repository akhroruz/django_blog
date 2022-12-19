import os

import django
from django.db.models import Q
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from apps.models import Post
import datetime


def cron_job():
    date = datetime.date.today()
    date_delta = datetime.timedelta(7)
    Post.objects.filter(Q(created_at__lt=date - date_delta), Q(status=Post.Status.CANCEL)).delete()


# faker = Faker()
# print(f'name: {faker.name()}')
# print(f'address: {faker.address()}')
# print(faker.file_name(category='image', extension='jpg'))
# print(f'text: {faker.text()}')
# print(faker.date_time_between_dates())
