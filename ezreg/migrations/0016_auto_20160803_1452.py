# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0015_payment_refunded'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='contact',
            field=models.TextField(default='UC Davis Bioinformatics Core, bioinformatics.core@ucdavis.edu'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/virtualenvs/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
    ]
