# Generated by Django 4.1.3 on 2022-11-29 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_remove_siteinfo_pic_alter_siteinfo_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteinfo',
            name='title',
        ),
    ]