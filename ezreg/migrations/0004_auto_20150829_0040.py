# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0003_event_advertise'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'UNPAID', max_length=10, choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid')])),
                ('paid_at', models.DateTimeField(null=True, blank=True)),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
            ],
        ),
        migrations.AddField(
            model_name='registration',
            name='price',
            field=models.ForeignKey(blank=True, to='ezreg.Price', null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='registered',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 29, 0, 40, 6, 485086, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='price',
            name='amount',
            field=models.DecimalField(max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='price',
            name='event',
            field=models.ForeignKey(related_name='prices', to='ezreg.Event'),
        ),
        migrations.AddField(
            model_name='payment',
            name='registration',
            field=models.ForeignKey(to='ezreg.Registration'),
        ),
    ]
