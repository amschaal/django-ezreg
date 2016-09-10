# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ezreg.models


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0016_auto_20160803_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='key',
            field=models.CharField(default=ezreg.models.id_generator, max_length=10),
        ),
    ]
