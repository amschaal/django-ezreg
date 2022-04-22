# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import ezreg.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mailqueue', '0002_mailermessage_reply_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(default=ezreg.models.id_generator, max_length=10, serialize=False, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=100, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('body', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('capacity', models.IntegerField(null=True, blank=True)),
                ('cancellation_policy', models.TextField(null=True, blank=True)),
                ('open_until', models.DateField()),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('address', models.TextField(null=True, blank=True)),
                ('advertise', models.BooleanField(default=False)),
                ('enable_waitlist', models.BooleanField(default=False)),
                ('enable_application', models.BooleanField(default=False)),
                ('waitlist_message', models.TextField(null=True, blank=True)),
                ('ical', models.FilePathField(path=b'/virtualenvs/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True)),
                ('form_fields', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
            options={
                'permissions': (('admin_event', 'Can modify event'), ('view_event', 'Can view event details and registrations')),
            },
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(blank=True)),
                ('heading', models.CharField(max_length=40)),
                ('body', models.TextField()),
                ('event', models.ForeignKey(related_name='pages', to='ezreg.Event', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EventProcessor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.ForeignKey(to='ezreg.Event', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OrganizerUserPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(max_length=10, choices=[(b'admin', b'Administer'), (b'view', b'View registrations')])),
                ('organizer', models.ForeignKey(related_name='user_permissions', to='ezreg.Organizer', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'UNPAID', max_length=10, choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid')])),
                ('paid_at', models.DateTimeField(null=True, blank=True)),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processor_id', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('config', jsonfield.fields.JSONField()),
                ('organizer', models.ForeignKey(to='ezreg.Organizer', on_delete=models.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=250, blank=True)),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('event', models.ForeignKey(related_name='prices', to='ezreg.Event', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.CharField(default=ezreg.models.id_generator, max_length=10, serialize=False, primary_key=True)),
                ('status', models.CharField(blank=True, max_length=25, null=True, choices=[(b'REGISTERED', b'Registered'), (b'PENDING_INCOMPLETE', b'Pending'), (b'WAITLIST_PENDING', b'Pending from waitlist'), (b'WAITLISTED', b'Waitlisted'), (b'WAITLIST_INCOMPLETE', b'Waitlist- incomplete'), (b'APPLIED_ACCEPTED', b'Application accepted'), (b'APPLIED', b'Applied'), (b'APPLY_INCOMPLETE', b'Application- incomplete'), (b'CANCELLED', b'Cancelled')])),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=50, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('test', models.BooleanField(default=False)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('email_messages', models.ManyToManyField(related_name='registrations', to='mailqueue.MailerMessage')),
                ('event', models.ForeignKey(related_name='registrations', to='ezreg.Event', on_delete=models.PROTECT)),
                ('price', models.ForeignKey(blank=True, to='ezreg.Price', null=True, on_delete=models.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='processor',
            field=models.ForeignKey(blank=True, to='ezreg.PaymentProcessor', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='payment',
            name='registration',
            field=models.OneToOneField(related_name='payment', to='ezreg.Registration', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='eventprocessor',
            name='processor',
            field=models.ForeignKey(to='ezreg.PaymentProcessor', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(to='ezreg.Organizer', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='event',
            name='payment_processors',
            field=models.ManyToManyField(to='ezreg.PaymentProcessor', through='ezreg.EventProcessor'),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('email', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizeruserpermission',
            unique_together=set([('organizer', 'user', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventpage',
            unique_together=set([('event', 'slug')]),
        ),
    ]
