from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput, ModelMultipleChoiceField, CheckboxSelectMultiple, Form, \
    EmailField
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.models import Comment, User, Post, Category, Message


class RegisterForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_password(self):
        password = self.data.get('password')
        confirm_password = self.data.get('confirm_password')
        if confirm_password != password:
            raise ValidationError('Parolni tekshiring!')
        return make_password(password)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'bio', 'image', 'password')


class CustomLoginForm(AuthenticationForm):
    def clean_password(self):
        username = self.data.get('username')
        password = self.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and not user.check_password(password):
            raise ValidationError('The password or username did not match')
        return password


class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ()


class CreatePostForm(ModelForm):
    category = ModelMultipleChoiceField(
        queryset=Category.objects.order_by('name'),
        label="Category",
        widget=CheckboxSelectMultiple
    )

    class Meta:
        model = Post
        fields = ('title', 'content', 'pic', 'category')


class ForgotPasswordForm(Form):
    email = EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('This profile is not registered')
        return email

    class Meta:
        model = User
        fields = ('email',)


# class ResetPasswordForm(SetPasswordForm):
#     pass
# class ResetPasswordForm(ModelForm):
#     password = CharField(max_length=255)
#     confirm_password = CharField(max_length=255)
#
#     def clean_password(self):
#         password = self.data.get('password')
#         confirm_password = self.data.get('confirm_password')
#         if password != confirm_password:
#             raise ValidationError('Parol xato!')
#         return password
#
#     class Meta:
#         model = User
#         fields = ('password',)


class MessageForm(ModelForm):
    name = CharField(max_length=255)
    message = CharField()

    class Meta:
        model = Message
        fields = ('name', 'message')


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio', 'image')


class ChangePasswordForm(Form):
    password = CharField(max_length=255)
    new_password = CharField(max_length=255)
    confirm_password = CharField(max_length=255)

    def clean_password(self):
        user = self.initial['request'].user
        password = self.cleaned_data.get('password')
        if not user.check_password(password):
            raise ValidationError('Eski parol xato')
        return password

    def clean_new_password(self):
        new_password = self.data.get('new_password')
        confirm_password = self.data.get('confirm_password')
        if new_password != confirm_password:
            raise ValidationError('Parol xato!')
        return new_password

    def save(self, user):
        new_password = self.cleaned_data.get('new_password')
        user.set_password(new_password)
        user.save()
