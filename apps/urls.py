from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.views import IndexView, AboutView, ContactView, PostListView, CustomLoginView, RegisterView, \
    DetailFormPostView, CreatePostView, ForgotPasswordPage, GeneratePdf

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('pdf', GeneratePdf.as_view(), name='make_pdf'),
    path('forgot-password/', ForgotPasswordPage.as_view(), name='forgot'),

    path('about', AboutView.as_view(), name='about'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('contact', ContactView.as_view(), name='contact'),
    path('blog-category', PostListView.as_view(), name='category'),
    path('post/<str:slug>', DetailFormPostView.as_view(), name='post_form_detail'),
    path('create-post', CreatePostView.as_view(), name='create-post'),
    path('', IndexView.as_view(), name='index'),
]
