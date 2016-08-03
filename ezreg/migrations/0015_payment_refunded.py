# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0014_auto_20160801_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='refunded',
            field=models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True),
        ),
    ]
