from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.views import IndexView, AboutView, ContactView, PostListView, CustomLoginView, RegisterView, \
    DetailFormPostView, CreatePostView, ChangePasswordPage, GeneratePdf, ActivateEmailView, ProfileView, \
    ForgotPasswordView, ResetPasswordView, SearchView

urlpatterns = (
    path('', IndexView.as_view(), name='index'),
    path('my-posts', PostListView.as_view(), name='mypost'),
    path('login', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uid>/<str:token>', ActivateEmailView.as_view(), name='confirm_mail'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordPage.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot'),
    path('reset/<str:uid>/<str:token>', ResetPasswordView.as_view(), name='reset'),

    path('search', csrf_exempt(SearchView.as_view()), name='search'),
    path('about', AboutView.as_view(), name='about'),
    path('contact', ContactView.as_view(), name='contact'),
    path('blog-category', PostListView.as_view(), name='category'),
    path('create-post', CreatePostView.as_view(), name='create_post'),
    path('pdf/<int:pk>', GeneratePdf.as_view(), name='make_pdf'),
    path('post/<str:slug>', DetailFormPostView.as_view(), name='post_form_detail'),
)
