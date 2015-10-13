# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ezreg.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='bcc',
            field=ezreg.fields.EmailListField(max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='cc',
            field=ezreg.fields.EmailListField(max_length=250, null=True, blank=True),
        ),
    ]
