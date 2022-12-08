from apps.models import Category, Post, Siteinfo


def context_category(request):
    return {
        'custom_categories': Category.objects.all()
    }


def context_post(request):
    return {
        'custom_posts': Post.objects.filter(status='active')
    }


def context_info(request):
    return {
        'custom_info': Siteinfo.objects.first()
    }


def context_trending_post(request):
    return {
        'trending_posts': Post.objects.filter(status='active')[:4]
    }
