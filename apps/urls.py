from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.views import IndexView, AboutView, ContactView, PostListView, CustomLoginView, RegisterView, \
    DetailFormPostView, CreatePostView, ForgotPasswordPage, ChangePasswordPage, GeneratePdf, ActivateEmailView, \
    ResetPasswordView, ProfileView

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordPage.as_view(), name='forgot'),
    path('change-password/', ChangePasswordPage.as_view(), name='change_password'),
    path('activate/<str:uid>/<str:token>', ActivateEmailView.as_view(), name='confirm_mail'),
    path('reset-password/<str:uid>/<str:token>', ResetPasswordView.as_view(), name='reset_mail'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),

    path('pdf/<int:pk>', GeneratePdf.as_view(), name='make_pdf'),
    path('about', AboutView.as_view(), name='about'),
    path('contact', ContactView.as_view(), name='contact'),
    path('blog-category', PostListView.as_view(), name='category'),
    path('post/<str:slug>', DetailFormPostView.as_view(), name='post_form_detail'),
    path('create-post', CreatePostView.as_view(), name='create-post'),

    path('', IndexView.as_view(), name='index'),
]
