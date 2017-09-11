# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0023_auto_20170829_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=django_bleach.models.BleachField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/data/virtualenv/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
    ]
