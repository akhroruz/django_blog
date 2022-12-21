import csv
from django.core.management.base import BaseCommand
from apps.models import Region, District


class Command(BaseCommand):
    help = 'Create regions or districts list'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, help='Regions or Districts')

    def handle(self, *args, **kwargs):
        _type = kwargs['type']
        if _type == 'region':
            with open('apps/static/regions.csv') as f:
                f.readline()
                reader = csv.reader(f)
                for row in reader:
                    _, created = Region.objects.get_or_create(
                        id=row[0],
                        name=row[1],
                    )
        elif _type == 'district':
            with open('apps/static/districts.csv') as f:
                f.readline()
                reader = csv.reader(f)
                for row in reader:
                    _, created = District.objects.get_or_create(
                        id=row[0],
                        name=row[1],
                        region_id=row[2]
                    )
