# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0002_auto_20151013_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='cc',
        ),
        migrations.AddField(
            model_name='event',
            name='from_addr',
            field=models.EmailField(max_length=50, null=True, blank=True),
        ),
    ]
