# Generated by Django 4.1.3 on 2022-12-10 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0012_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name_plural': 'Xabarlar'},
        ),
        migrations.AddField(
            model_name='message',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]