# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-25 05:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_auto_20160625_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='cash_recieved',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='eft_added',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='eft_loss',
            field=models.FloatField(blank=True),
        ),
    ]
