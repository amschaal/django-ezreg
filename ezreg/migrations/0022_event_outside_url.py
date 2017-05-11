# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0021_registration_admin_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='outside_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
