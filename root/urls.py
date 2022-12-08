from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import STATIC_URL, STATIC_ROOT, MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(STATIC_URL, document_root=STATIC_ROOT) + static(MEDIA_URL, document_root=MEDIA_ROOT)
