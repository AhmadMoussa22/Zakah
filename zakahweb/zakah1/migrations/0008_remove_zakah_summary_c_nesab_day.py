# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-05-28 20:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zakah1', '0007_auto_20200528_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zakah_summary_c',
            name='nesab_day',
        ),
    ]
