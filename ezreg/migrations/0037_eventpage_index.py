# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-01-14 21:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0036_auto_20190506_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventpage',
            name='index',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
