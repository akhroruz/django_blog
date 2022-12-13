from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('apps', '0015_alter_message_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='media/profile/default.jpg', upload_to='profile/'),
        ),
    ]
