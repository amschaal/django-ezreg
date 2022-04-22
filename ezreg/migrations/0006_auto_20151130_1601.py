# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0005_auto_20151015_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='capacity',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/data/virtualenv/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(related_name='events', to='ezreg.Organizer', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(blank=True, unique=True, max_length=100, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
    ]
