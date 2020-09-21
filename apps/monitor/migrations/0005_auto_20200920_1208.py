# Generated by Django 3.0.7 on 2020-09-20 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_auto_20200915_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboard',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitor.User'),
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=200)),
                ('message', models.CharField(max_length=200)),
                ('hostname', models.CharField(max_length=200)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('vManager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitor.VManager')),
            ],
        ),
    ]
