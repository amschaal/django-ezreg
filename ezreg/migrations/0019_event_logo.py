# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0018_auto_20170406_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='logo',
            field=models.ImageField(null=True, upload_to=b'logos/', blank=True),
        ),
    ]
