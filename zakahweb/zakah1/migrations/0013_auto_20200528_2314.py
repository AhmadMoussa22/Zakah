# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-05-28 21:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zakah1', '0012_auto_20200528_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zakah_register_c',
            name='deserve_day',
            field=models.DateField(default=datetime.date(2000, 2, 2)),
        ),
    ]