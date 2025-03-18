# Generated by Django 5.1.6 on 2025-03-04 14:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('oaauth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='informs', related_query_name='informs', to=settings.AUTH_USER_MODEL)),
                ('departments', models.ManyToManyField(related_name='informs', related_query_name='informs', to='oaauth.oadepartment')),
            ],
            options={
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='InformRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_time', models.DateTimeField(auto_now_add=True)),
                ('inform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads', related_query_name='reads', to='inform.inform')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reads', related_query_name='reads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('inform', 'user')},
            },
        ),
    ]
