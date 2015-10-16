# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0004_auto_20151015_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizeruserpermission',
            name='permission',
            field=models.CharField(max_length=25, choices=[(b'admin', b'Administer'), (b'view', b'View registrations'), (b'manage_processors', b'Manage payment processors')]),
        ),
        migrations.AlterField(
            model_name='paymentprocessor',
            name='organizer',
            field=models.ForeignKey(related_name='payment_processors', to='ezreg.Organizer'),
        ),
    ]
