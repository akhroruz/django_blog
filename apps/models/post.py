from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Model, CharField, SlugField, ForeignKey, DateTimeField, \
    ManyToManyField, SET_NULL, TextChoices, Manager
from django.utils.html import format_html
from django.utils.text import slugify
from django_resized import ResizedImageField


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
    author = ForeignKey('apps.User', SET_NULL, null=True, blank=True)
    pic = ResizedImageField(upload_to='posts/')
    category = ManyToManyField('apps.Category')
    created_at = DateTimeField(auto_now_add=True)

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

    # @property
    # def comment_count(self):
    #     return self.comment_set.count()

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
