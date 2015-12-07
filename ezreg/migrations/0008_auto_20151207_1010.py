# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0007_auto_20151204_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default=b'UNPAID', max_length=20, choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid'), (b'CANCELLED', b'Cancelled'), (b'INVALID_AMOUNT', b'Invalid Amount')]),
        ),
    ]
