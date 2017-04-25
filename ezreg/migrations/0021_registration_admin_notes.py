# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0020_auto_20170406_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='admin_notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
