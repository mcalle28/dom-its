# Generated by Django 3.0.7 on 2020-11-05 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0011_auto_20201027_1125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='webhooklog',
            old_name='message',
            new_name='siteId',
        ),
        migrations.AddField(
            model_name='webhooklog',
            name='inDia',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
