# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0002_remove_event_advertise'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='advertise',
            field=models.BooleanField(default=False),
        ),
    ]
