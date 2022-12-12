from apps.models import Category, Post, SiteInfo


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
    return {
        # 'trending_posts': Post.objects.filter(status='active')[:4]
        # 'trending_posts': PostView
    }