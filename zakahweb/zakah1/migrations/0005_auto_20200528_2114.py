# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-05-28 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zakah1', '0004_auto_20200528_0119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zakah_register_c',
            name='deserve_day',
            field=models.DateField(default=(1111, 1, 1)),
        ),
        migrations.AlterField(
            model_name='zakah_register_c',
            name='start_day',
            field=models.DateField(default=(1111, 1, 1)),
        ),
    ]