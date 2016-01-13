# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0011_auto_20160111_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='display_address',
            field=models.BooleanField(default=True),
        ),
    ]
