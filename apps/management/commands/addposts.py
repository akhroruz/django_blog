import csv

from django.core.management.base import BaseCommand
from faker.utils.text import slugify

from apps.models import Region, District, Post
from faker import Faker


class Command(BaseCommand):
    help = 'Create blogs'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of posts count.')

    def handle(self, *args, **kwargs):
        faker = Faker()
        total = kwargs['total']
        for _ in range(total):
            _, created = Post.objects.get_or_create(
                status=Post.Status.ACTIVE,
                created_at=faker.date_time_between_dates(),
                author_id=1,
                content=faker.sentence(1000),
                title=faker.text(100),
                pic='posts/7-21-1280x851.jpg',
                slug=slugify(faker.text(100))
            )
