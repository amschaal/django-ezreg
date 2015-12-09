# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0008_auto_20151207_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='coupon_code',
            field=models.CharField(max_length=25, unique=True, null=True, blank=True),
        ),
    ]
