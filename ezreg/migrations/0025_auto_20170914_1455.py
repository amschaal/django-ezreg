# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0024_auto_20170911_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='coupon_code',
            field=models.CharField(max_length=25, null=True, blank=True),
        ),
    ]
