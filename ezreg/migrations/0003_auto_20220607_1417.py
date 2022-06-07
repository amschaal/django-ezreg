# Generated by Django 2.2.28 on 2022-06-07 14:17

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ezreg', '0002_auto_20220607_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='form_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentprocessor',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='registration',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]