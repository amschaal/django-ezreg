# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-06-05 20:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0040_event_department_field'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'permissions': (('admin_event', 'Can modify event'), ('view_event', 'Can view event details and registrations'), ('bill_event', 'Can bill events'))},
        ),
    ]
