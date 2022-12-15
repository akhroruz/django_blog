from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView

from apps.forms import CreateCommentForm, CustomLoginForm, CreatePostForm, RegisterForm, ForgotPasswordForm, \
    MessageForm, ProfileForm, ChangePasswordForm
from apps.models import Category, Post, SiteInfo, Comment, PostView, User
from apps.utils.make_pdf import render_to_pdf
from apps.utils.tasks import send_to_gmail
from apps.utils.token import account_activation_token


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


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'apps/auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        if url := self.request.POST.get('url'):
            return HttpResponseRedirect(url)
        return res


class RegisterView(FormView):
    template_name = 'apps/auth/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        if user:
            user = authenticate(username=user.username, password=user.password)
            if user:
                login(self.request, user)
        current_site = get_current_site(self.request)
        send_to_gmail.apply_async(args=[form.data.get('email'), current_site.domain])
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('login')
        return super().get(request, *args, **kwargs)


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
        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'apps/auth/profile.html'
    queryset = User.objects.all()
    success_url = reverse_lazy('profile')
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('login')
        self.object = self.request.user
        context = self.get_context_data(object=self.object, form=self.form_class)
        return self.render_to_response(context)
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ChangePasswordPage(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        username = request.user.username
        user = request.user
        form = ChangePasswordForm(request.POST, initial={'request': request})
        if form.is_valid():
            form.save(request.user)
            password = form.data.get('new_password')
            user = authenticate(username=username, password=password)
            login(request, user)
        return redirect('profile', user.pk)


class ForgotPasswordView(FormView):
    template_name = 'apps/auth/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        current_site = get_current_site(self.request)
        send_to_gmail.apply_async(args=[form.data.get('email'), current_site.domain, 'reset'])
        return super().form_valid(form)


class ResetPasswordView(TemplateView):
    template_name = 'apps/auth/reset_password.html'

    def get_user(self, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception as e:
            user = None
        return user, user and account_activation_token.check_token(user, token)

    def get(self, request, *args, **kwargs):
        user, is_valid = self.get_user(**kwargs)
        if not is_valid:
            return HttpResponse('Link not found')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user, is_valid = self.get_user(**kwargs)
        if is_valid:
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        return HttpResponse('Link not found')
