# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0006_auto_20151130_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='external_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/virtualenvs/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default=b'UNPAID', max_length=10, choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid'), (b'CANCELLED', b'Cancelled'), (b'INVALID_AMOUNT', b'Invalid Amount')]),
        ),
    ]
