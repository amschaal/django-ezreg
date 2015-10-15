# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0003_auto_20151013_1502'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([]),
        ),
    ]
