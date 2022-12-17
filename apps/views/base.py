from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
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
            'posts': list(Post.objects.filter(title__icontains=like).values('title', 'pic', 'slug'))
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
        data = {
            'post': post,
        }
        pdf = render_to_pdf('make_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class PostListView(ListView):
    queryset = Post.active.all()
    template_name = 'apps/blog-category.html'
    paginate_by = 4
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        slug = self.request.GET.get('category')
        qs = self.get_queryset()
        context['posts'] = qs
        context['category'] = Category.objects.filter(slug=slug).first()
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
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
        context['comments'] = Comment.objects.filter(post__slug=self.kwargs.get('slug'))
        context['views'] = PostView.objects.filter(post__slug=self.kwargs.get('slug')).count()
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

