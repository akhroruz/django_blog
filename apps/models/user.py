from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ImageField, TextField, EmailField

from apps.managers import UserManager


class User(AbstractUser):
    phone = CharField(max_length=20, blank=True)
    bio = TextField(null=True, blank=True)
    email = EmailField(max_length=255, unique=True)
    image = ImageField(upload_to='profile/', default='media/profile/default.jpg')

    objects = UserManager()

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name_plural = 'Userlar'
