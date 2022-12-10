from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import ListView, DetailView, FormView, TemplateView

from apps.forms import CreateCommentForm, CustomLoginForm, CreatePostForm, RegisterForm, ForgotPasswordForm
from apps.models import Category, Post, Siteinfo, Comment, PostView, User
from apps.utils.tasks import send_to_gmail
from apps.utils.token import account_activation_token


class IndexView(ListView):
    queryset = Category.objects.all()
    context_object_name = 'categories'
    template_name = 'apps/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['posts'] = Post.objects.filter(status='active').order_by('-created_at')[:4]
        return context


class PostListView(ListView):
    queryset = Post.objects.filter(status='active').order_by('-created_at')
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
    model = Siteinfo
    context_object_name = 'about'


class ContactView(TemplateView):
    template_name = 'apps/contact.html'


class DetailFormPostView(FormView, DetailView):
    template_name = 'apps/post.html'
    queryset = Post.objects.all()
    context_object_name = 'post'
    form_class = CreateCommentForm

    def get_queryset(self):
        # Post.objects.filter(slug=self.kwargs.get('slug')).update(view=F('view') + 1)
        PostView.objects.create(post_id=Post.objects.filter(slug=self.kwargs.get('slug')).first().pk)
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


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'apps/auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('index')


class RegisterView(FormView):
    template_name = 'apps/auth/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('login')

    # def form_valid(self, form):
    #     user = form.save()
    #     if user is not None:
    #         login(self.request, user)
    #     return super().form_valid(form)
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        current_site = get_current_site(self.request)
        send_to_gmail(form.data.get('email'), current_site.domain, 'register')
        messages.add_message(
            self.request,
            level=messages.WARNING,
            message='Successfully send your email, Please activate your profile'
        )

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ForgotPasswordPage(FormView):
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login')
    template_name = 'apps/auth/forgot_password.html'

    def form_valid(self, form):
        current_site = get_current_site(self.request)
        send_to_gmail(form.data.get('email'), current_site.domain, 'forgot')
        return super().form_valid(form)


class ActivateEmailView(TemplateView):
    template_name = 'apps/auth/confirm_mail.html'

    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message="Your account successfully activated!"
            )
            return redirect('index')
        else:
            return HttpResponse('Activation link is invalid!')


class CreatePostView(LoginRequiredMixin, FormView):
    template_name = 'apps/create-post.html'
    form_class = CreatePostForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)
