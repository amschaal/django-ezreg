# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0012_event_display_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='order',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default=b'UNPAID', max_length=20, choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid'), (b'CANCELLED', b'Cancelled'), (b'INVALID_AMOUNT', b'Invalid Amount'), (b'ERROR', b'Error')]),
        ),
    ]
