from datetime import datetime

from django.db.models import Count
from future.backports.datetime import timedelta

from apps.models import Category, Post, SiteInfo, PostView


def context_category(request):
    return {
        'custom_categories': Category.objects.all()
    }


def context_post(request):
    return {
        'custom_posts': Post.active.all()
    }


def context_info(request):
    return {
        'custom_info': SiteInfo.objects.first()
    }


def context_trending_post(request):
    last = datetime.now() - timedelta(days=30)
    posts_id = PostView.objects.filter(created_at__gt=last).values_list('post_id', 'created_at').annotate(
        count=Count('post_id')).order_by('count', 'created_at')[:5]
    return {
        'trending_posts': Post.objects.filter(id__in=[i[0] for i in posts_id])
    }