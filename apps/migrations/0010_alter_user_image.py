# Generated by Django 4.1.3 on 2022-12-04 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_alter_category_options_alter_comment_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='default-avatar.png', upload_to='profile/'),
        ),
    ]