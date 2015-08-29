# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ezreg.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(default=ezreg.models.id_generator, max_length=10, serialize=False, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=100, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('capacity', models.IntegerField(null=True, blank=True)),
                ('cancellation_policy', models.TextField(null=True, blank=True)),
                ('open_until', models.DateField(null=True, blank=True)),
                ('advertise', models.DateField(default=False)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'permissions': (('admin_event', 'Can modify event'), ('view_event', 'Can view event details and registrations')),
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=250, blank=True)),
                ('amount', models.DecimalField(max_digits=6, decimal_places=2)),
                ('hidden', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to='ezreg.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('institution', models.CharField(max_length=100)),
                ('group_name', models.CharField(max_length=100)),
                ('special_requests', models.TextField()),
                ('event', models.ForeignKey(to='ezreg.Event')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('email', 'event')]),
        ),
    ]
