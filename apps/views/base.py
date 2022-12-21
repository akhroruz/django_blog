import os

import qrcode
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView

from apps.forms import MessageForm, CreateCommentForm
from apps.models import Post, Category, SiteInfo, PostView, Comment
from apps.utils.make_pdf import render_to_pdf


class SearchView(View):
    def post(self, request, *args, **kwargs):
        like = request.POST.get('like')
        data = {
            'posts': list(Post.objects.filter(title__icontains=like).values('title', 'pic', 'slug')),
            'domain': get_current_site(request)
        }
        return JsonResponse(data)


class IndexView(ListView):
    queryset = Category.objects.all()
    context_object_name = 'categories'
    template_name = 'apps/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['posts'] = Post.active.all()[:4]
        return context


class GeneratePdf(DetailView):
    slug_url_kwarg = 'pk'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs.get('pk'))
        url = f'{get_current_site(request)}/post/{post.slug}'

        img = qrcode.make(url)
        img.save(post.slug + '.png')

        data = {
            'post': post,
            'qrcode': f'{os.getcwd()}/{post.slug}.png'
        }
        print(os.getcwd())
        pdf = render_to_pdf('make_pdf.html', data)
        os.remove(f'{post.slug}.png')
        return HttpResponse(pdf, content_type='application/pdf')


class PostListView(ListView):
    queryset = Post.active.all()
    template_name = 'apps/blog-category.html'
    paginate_by = 4
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        pagination = context['page_obj']
        paginator = pagination.paginator
        page = pagination.number
        left = int(page) - 4
        if left < 1:
            left = 1
        right = int(page) + 5
        if right > paginator.num_pages:
            right = paginator.num_pages + 1
        context['pagination_range'] = range(left, right)
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        if self.request.path.split('/')[-1] == 'my-posts':
            return qs.filter(author=self.request.user.pk)
        if category := self.request.GET.get('category'):
            return qs.filter(category__slug=category)
        return qs


class AboutView(ListView):
    template_name = 'apps/about.html'
    model = SiteInfo
    context_object_name = 'about'


class ContactView(FormView):
    template_name = 'apps/contact.html'
    form_class = MessageForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class DetailFormPostView(FormView, DetailView):
    template_name = 'apps/post.html'
    queryset = Post.objects.all()
    context_object_name = 'post'
    form_class = CreateCommentForm

    def get_queryset(self):
        PostView.objects.create(post=Post.objects.filter(slug=self.kwargs.get('slug')).first())
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['comments'] = Comment.objects.filter(post__slug=slug)
        context['views'] = PostView.objects.filter(post__slug=slug).count()
        return context

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        post = get_object_or_404(Post, slug=slug)
        data = {
            'post': post,
            'author': request.user,
            'text': request.POST.get('text'),
        }
        form = self.form_class(data)
        if form.is_valid():
            form.save()
        return redirect('post_form_detail', slug)


def page_not_found(request, exception):
    response = render(request, '404.html', status=404)
    return response
