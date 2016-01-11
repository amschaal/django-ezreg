# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0010_auto_20151208_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='expiration_time',
            field=models.PositiveSmallIntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='event',
            name='body',
            field=django_bleach.models.BleachField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='cancellation_policy',
            field=django_bleach.models.BleachField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(unique=True, max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='body',
            field=django_bleach.models.BleachField(),
        ),
    ]
