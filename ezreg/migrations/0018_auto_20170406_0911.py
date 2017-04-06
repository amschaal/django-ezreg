# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0017_registration_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/data/virtualenv/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
    ]
