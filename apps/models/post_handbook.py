from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.postgres.fields import ArrayField
from django.db.models import Model, CharField, ImageField, SlugField, ForeignKey, CASCADE, DateTimeField, \
    TextField, EmailField, BooleanField, PROTECT
from django.utils.text import slugify


class SiteInfo(Model):
    description = RichTextUploadingField()
    about = TextField()
    location = CharField(max_length=255)
    email = EmailField(max_length=255)
    phone = CharField(max_length=20, blank=True)
    social = ArrayField(CharField(max_length=255))

    class Meta:
        verbose_name_plural = 'Sayt haqida'
        verbose_name = 'Sayt haqida'

    def __str__(self):
        return self.about[:15]


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
            while Category.objects.filter(slug=self.slug).exists():
                slug = Category.objects.filter(slug=self.slug).first().slug
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


class Comment(Model):
    text = TextField()
    post = ForeignKey('apps.Post', CASCADE)
    author = ForeignKey('apps.User', CASCADE)
    created_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Izoh'
        verbose_name_plural = 'Izohlar'


class PostView(Model):
    post = ForeignKey('apps.Post', CASCADE)
    created_at = DateTimeField(auto_now_add=True)


class Message(Model):
    author = ForeignKey('apps.User', PROTECT)
    name = CharField(max_length=255)
    message = TextField()
    status = BooleanField(default=False)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'

    def __str__(self):
        return self.name


class Region(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region', CASCADE)

    def __str__(self):
        return self.name
