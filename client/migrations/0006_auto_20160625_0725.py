# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-25 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_auto_20160625_0724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='date_sold',
            field=models.CharField(max_length=100),
        ),
    ]
