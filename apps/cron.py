from datetime import datetime, timedelta

from apps.models import Post


def my_scheduled_job():
    date = datetime.today()
    start_week = date - timedelta(date.weekday())
    end_week = start_week + timedelta(7)
    entries = Post.objects.filter(created_at__range=[start_week, end_week])
    return entries
