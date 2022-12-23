from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, UpdateView, FormView

from apps.forms import ProfileForm, ChangePasswordForm, ForgotPasswordForm, RegisterForm, \
    CreatePostForm, CustomLoginForm
from apps.models import User
from apps.utils.tasks import send_to_gmail
from apps.utils.token import account_activation_token


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'apps/auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    next_page = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        if url := self.request.POST.get('url'):
            return HttpResponseRedirect(url)
        return result


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

            return redirect('change_password')
        return HttpResponse('Link not found')

# class TwilioView(View):
#     def get(self, request, *args, **kwargs):
#         message_to_broadcast = (
#             "Have you played the incredible TwilioQuest yet? Grab it here: https://www.twilio.com/quest")
#         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#         for recipient in settings.SMS_BROADCAST_TO_NUMBERS:
#             if recipient:
#                 client.messages.create(to=recipient,
#                                        from_=settings.TWILIO_NUMBER,
#                                        body=message_to_broadcast)
#         return HttpResponse("messages sent!", 200)
