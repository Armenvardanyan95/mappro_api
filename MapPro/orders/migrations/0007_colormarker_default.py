# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-29 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20170826_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='colormarker',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]