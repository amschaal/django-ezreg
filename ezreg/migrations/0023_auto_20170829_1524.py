# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0022_event_outside_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='coupon_code',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='price',
            unique_together=set([('event', 'coupon_code')]),
        ),
    ]
