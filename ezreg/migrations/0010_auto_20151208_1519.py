# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0009_price_coupon_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='coupon_code',
            field=models.CharField(max_length=25, unique=True, null=True),
        ),
    ]
