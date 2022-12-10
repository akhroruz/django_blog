from datetime import datetime

from django.test import TestCase
t = datetime.strptime('2022-12-09 10:38:25.423811 +00:00', )

n = datetime.now().month
print(n - t.day)