# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0019_event_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/virtualenvs/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]
