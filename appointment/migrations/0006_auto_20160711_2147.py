# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-11 17:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_auto_20160711_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='input_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.Trainer'),
        ),
    ]