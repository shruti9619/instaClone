# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-23 07:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0008_sessiontoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='Anonymous', max_length=255),
        ),
    ]
