# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-11 17:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0009_auto_20160707_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='sold_by',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='client.Trainer'),
        ),
    ]
