# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ezreg', '0013_auto_20160218_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='registered_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/data/virtualenv/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
    ]
