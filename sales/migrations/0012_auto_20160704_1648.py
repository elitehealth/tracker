# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-04 12:48
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_auto_20160625_1054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='record',
            name='sold_by',
        ),
        migrations.AddField(
            model_name='record',
            name='consults_attended',
            field=models.FloatField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='record',
            name='consults_closed',
            field=models.FloatField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
