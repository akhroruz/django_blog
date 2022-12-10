from django.contrib.admin import ModelAdmin, register
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from apps.models import Category, Post, Siteinfo


@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'post_count')
    exclude = ('slug',)


@register(Post)
class PostAdmin(ModelAdmin):
    search_fields = ('category__name', 'title')
    list_display = ('title', 'categories', 'is_active', 'post_pic', 'created_at', 'status_buttons')
    exclude = ('slug', 'view', 'author', 'status')
    list_filter = ('category', 'created_at')
    change_form_template = "admin/custom/change_form.html"

    def response_change(self, request, obj):
        post = request.POST
        if "_cancel" in post:
            self.get_queryset(request).filter(pk=obj.pk).update(status='cancel')
            self.message_user(request, "The post has been cancelled.")
            return HttpResponseRedirect('../')
        elif '_active' in post:
            self.get_queryset(request).filter(pk=obj.pk).update(status='active')
            self.message_user(request, "The post has been actived.")
            return HttpResponseRedirect('../')
        elif '_preview' in post:
            return redirect('post_form_detail', slug=obj.slug)
        return super().response_change(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('cancel/<int:id>', self.cancel), path('active/<int:id>', self.active)]
        return my_urls + urls

    def active(self, request, id):
        post = Post.objects.filter(id=id).first()
        post.status = Post.Status.ACTIVE
        post.save()
        return HttpResponseRedirect('../')

    def cancel(self, request, id):
        post = Post.objects.filter(id=id).first()
        post.status = Post.Status.CANCEL
        post.save()
        return HttpResponseRedirect('../')

    def is_active(self, obj):
        data = {
            'pending': '<i class="fa-solid fa-hourglass-start" style="color: grey; font-size: 1em;margin-top: 8px; margin: auto;"></i>',
            'active': '<i class="fa-solid fa-check" style="color: green; font-size: 1em;margin-top: 8px; margin: auto;"></i>',
            'cancel': '<i class="fa-solid fa-circle-xmark"  style="color: red; font-size: 1em;margin-top: 8px; margin: auto;"></i>'
        }
        return format_html(data[obj.status])

    def categories(self, obj: Post):
        lst = []
        for i in obj.category.all():
            lst.append(f'''<a href="{reverse('admin:apps_category_change', args=(i.pk,))}">{i.name}</a>''')
        return format_html(', '.join(lst))

    def post_pic(self, obj: Post):
        return format_html(f'<img style="border-radius: 5px;" width="100px" height="30px" src="{obj.pic.url}"/>')

    is_active.short_description = 'Status'


@register(Siteinfo)
class AboutAdmin(ModelAdmin):
    pass
