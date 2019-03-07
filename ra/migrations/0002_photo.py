# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-03-07 08:35
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ra', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('sitename', models.CharField(max_length=30)),
                ('prefecture', models.CharField(max_length=30)),
                ('country', models.CharField(max_length=30)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('path', models.CharField(max_length=100)),
                ('path_resized', models.CharField(max_length=100)),
                ('path_resized_480', models.CharField(max_length=100)),
                ('path_resized_1200', models.CharField(max_length=100)),
                ('landmark', models.CharField(blank=True, max_length=30)),
                ('latitude', models.FloatField(blank=True)),
                ('longitude', models.FloatField(blank=True)),
                ('score', models.FloatField(blank=True)),
                ('is_api_called', models.BooleanField(default=False)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), blank=True, default=list, size=None)),
            ],
        ),
    ]
