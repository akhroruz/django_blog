from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput, ModelMultipleChoiceField, CheckboxSelectMultiple, Form, \
    EmailField

from apps.models import Comment, User, Post, Category


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
