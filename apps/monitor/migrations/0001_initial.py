# Generated by Django 3.0.7 on 2020-07-12 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userName', models.CharField(max_length=64)),
                ('password', models.CharField(max_length=64)),
                ('isAdmin', models.BooleanField(default=False)),
            ],
        ),
    ]
