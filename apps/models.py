from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db.models import Model, CharField, ImageField, SlugField, ForeignKey, CASCADE, DateTimeField, \
    ManyToManyField, SET_NULL, TextField, EmailField, TextChoices, BooleanField, IntegerField, PROTECT, Manager
from django.utils.html import format_html
from django.utils.text import slugify
from django_resized import ResizedImageField


class SiteInfo(Model):
    description = RichTextUploadingField()
    about = TextField()
    location = CharField(max_length=255)
    email = EmailField(max_length=255)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone = CharField(max_length=20, blank=True)
    social = ArrayField(CharField(max_length=255))

    class Meta:
        verbose_name_plural = 'Sayt haqida'
        verbose_name = 'Sayt haqida'

    def __str__(self):
        return self.about[:15]


class User(AbstractUser):
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone = CharField(max_length=20, blank=True)
    bio = TextField(null=True, blank=True)
    email = EmailField(max_length=255, unique=True, blank=True)
    is_active = BooleanField(default=False)
    image = ImageField(upload_to='profile/', default='media/profile/default.jpg')

    class Meta:
        verbose_name_plural = 'Userlar'


class Category(Model):
    name = CharField(max_length=255)
    image = ImageField(upload_to='category/')
    slug = SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Post.objects.filter(slug=self.slug).exists():
                slug = Post.objects.filter(slug=self.slug).first().slug
                if '-' in slug:
                    try:
                        if slug.split('-')[-1] in self.name:
                            self.slug += '-1'
                        else:
                            self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                    except:
                        self.slug = slug + '-1'
                else:
                    self.slug += '-1'
            super().save(*args, **kwargs)

    @property
    def post_count(self):
        return self.post_set.filter(status='active').count()

    def __str__(self):
        return self.name


class ActivePostsManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.ACTIVE)


class Post(Model):
    class Status(TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        ACTIVE = 'active', 'Faol'
        CANCEL = 'cancel', 'Rad etilgan'

    title = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True)
    content = RichTextUploadingField()
    status = CharField(max_length=25, choices=Status.choices, default=Status.PENDING)
    author = ForeignKey(User, SET_NULL, null=True, blank=True)
    pic = ResizedImageField(upload_to='posts/')
    view = IntegerField(default=0)
    category = ManyToManyField(Category)
    created_at = DateTimeField(auto_now=True)

    objects = Manager()
    active = ActivePostsManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            while Post.objects.filter(slug=self.slug).exists():
                slug = Post.objects.filter(slug=self.slug).first().slug
                if '-' in slug:
                    try:
                        if slug.split('-')[-1] in self.title:
                            self.slug += '-1'
                        else:
                            self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                    except:
                        self.slug = slug + '-1'
                else:
                    self.slug += '-1'
        super().save(*args, **kwargs)

    @property
    def comment_count(self):
        return self.comment_set.count()

    def status_buttons(self):  # noqa
        if self.status == Post.Status.PENDING:
            return format_html(
                f'''<a href="active/{self.pk}" class="button">Active</a>
                <a href="cancel/{self.pk}" class="button">Cancel</a>'''
            )
        return format_html('''<b class="button">Ko'rib chiqilgan</b>''')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Postlar'


class Comment(Model):
    text = TextField()
    post = ForeignKey(Post, CASCADE)
    author = ForeignKey(User, CASCADE)
    created_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Izoh'
        verbose_name_plural = 'Izohlar'


class PostView(Model):
    post = ForeignKey(Post, CASCADE)
    created_at = DateTimeField(auto_now=True)


class Message(Model):
    author = ForeignKey(User, PROTECT)
    name = CharField(max_length=255)
    message = TextField()
    status = BooleanField(default=False)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'

    def __str__(self):
        return self.name
