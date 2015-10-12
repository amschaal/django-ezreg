# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import ezreg.models
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'ezreg', '0001_initial'), (b'ezreg', '0002_remove_event_advertise'), (b'ezreg', '0003_event_advertise'), (b'ezreg', '0004_auto_20150829_0040'), (b'ezreg', '0005_auto_20150831_1824'), (b'ezreg', '0006_event_body'), (b'ezreg', '0007_auto_20150831_2252'), (b'ezreg', '0008_auto_20150901_0008'), (b'ezreg', '0009_payment_data'), (b'ezreg', '0010_payment_processor'), (b'ezreg', '0011_auto_20150901_2340'), (b'ezreg', '0012_auto_20150903_1904'), (b'ezreg', '0013_auto_20150904_1803'), (b'ezreg', '0014_auto_20150904_2351'), (b'ezreg', '0015_auto_20150905_0002'), (b'ezreg', '0016_auto_20150905_0007'), (b'ezreg', '0017_auto_20150910_0028'), (b'ezreg', '0018_remove_event_from_email'), (b'ezreg', '0019_auto_20150911_2303'), (b'ezreg', '0020_auto_20150912_0024'), (b'ezreg', '0021_auto_20150916_2256'), (b'ezreg', '0022_auto_20150917_1236'), (b'ezreg', '0023_event_enable_application'), (b'ezreg', '0024_auto_20150929_1140'), (b'ezreg', '0025_registration_email_messages'), (b'ezreg', '0026_auto_20151002_1045'), (b'ezreg', '0027_event_form_fields'), (b'ezreg', '0028_auto_20151006_1031'), (b'ezreg', '0029_auto_20151006_1455'), (b'ezreg', '0030_organizer_organizeruserpermission'), (b'ezreg', '0031_organizer_slug'), (b'ezreg', '0032_organizeruserpermission_organizer'), (b'ezreg', '0033_auto_20151007_1428'), (b'ezreg', '0034_auto_20151007_1441'), (b'ezreg', '0035_auto_20151007_1641'), (b'ezreg', '0036_auto_20151009_1605'), (b'ezreg', '0037_auto_20151009_1606'), (b'ezreg', '0038_registration_test')]

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mailqueue', '0002_mailermessage_reply_to'),
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
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('event', models.ForeignKey(related_name='prices', to='ezreg.Event')),
                ('end_date', models.DateField(null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
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
        migrations.RemoveField(
            model_name='event',
            name='advertise',
        ),
        migrations.AddField(
            model_name='event',
            name='advertise',
            field=models.BooleanField(default=False),
        ),
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
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='registration',
            field=models.OneToOneField(related_name='payment', to='ezreg.Registration'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='id',
            field=models.CharField(default=ezreg.models.id_generator, max_length=10, serialize=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='event',
            name='body',
            field=models.TextField(default='Event body...'),
            preserve_default=False,
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
                ('group', models.ForeignKey(to='auth.Group')),
            ],
        ),
        migrations.AlterField(
            model_name='registration',
            name='event',
            field=models.ForeignKey(related_name='registrations', to='ezreg.Event'),
        ),
        migrations.CreateModel(
            name='EventProcessor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(unique=True, max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='eventprocessor',
            name='event',
            field=models.ForeignKey(to='ezreg.Event'),
        ),
        migrations.AddField(
            model_name='eventprocessor',
            name='processor',
            field=models.ForeignKey(to='ezreg.PaymentProcessor'),
        ),
        migrations.AddField(
            model_name='event',
            name='payment_processors',
            field=models.ManyToManyField(to=b'ezreg.PaymentProcessor', through='ezreg.EventProcessor'),
        ),
        migrations.AddField(
            model_name='payment',
            name='data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='processor',
            field=models.ForeignKey(blank=True, to='ezreg.PaymentProcessor', null=True),
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, blank=True)),
                ('heading', models.CharField(max_length=40)),
                ('body', models.TextField()),
                ('event', models.ForeignKey(to='ezreg.Event')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='eventpage',
            unique_together=set([('event', 'slug')]),
        ),
        migrations.AddField(
            model_name='event',
            name='enable_waitlist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='waitlist_message',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='status',
            field=models.CharField(blank=True, max_length=25, null=True, choices=[(b'REGISTERED', b'Registered'), (b'PENDING_INCOMPLETE', b'Pending'), (b'WAITLIST_PENDING', b'Pending from waitlist'), (b'WAITLISTED', b'Waitlisted'), (b'WAITLIST_INCOMPLETE', b'Waitlist- incomplete'), (b'APPLIED_ACCEPTED', b'Application accepted'), (b'APPLIED', b'Applied'), (b'APPLY_INCOMPLETE', b'Application- incomplete'), (b'CANCELLED', b'Cancelled')]),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='event',
            field=models.ForeignKey(related_name='pages', to='ezreg.Event'),
        ),
        migrations.AlterField(
            model_name='event',
            name='open_until',
            field=models.DateField(default=datetime.datetime(2015, 9, 4, 23, 51, 55, 701243, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registration',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='first_name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='group_name',
            new_name='department',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='department',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='institution',
        ),
        migrations.AlterField(
            model_name='registration',
            name='last_name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='registration',
            name='special_requests',
        ),
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='address',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='enable_application',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='ical',
            field=models.FilePathField(path=b'/virtualenvs/django-ezreg/include/ezreg/files', null=True, match=b'*.ics', blank=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='email_messages',
            field=models.ManyToManyField(related_name='registrations', to=b'mailqueue.MailerMessage'),
        ),
        migrations.AddField(
            model_name='event',
            name='form_fields',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='data',
            field=jsonfield.fields.JSONField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('slug', models.SlugField(default='slug', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizerUserPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', models.CharField(max_length=10, choices=[(b'admin', b'Administer'), (b'view', b'View registrations')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('organizer', models.ForeignKey(related_name='user_permissions', to='ezreg.Organizer')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(default=1, to='ezreg.Organizer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentprocessor',
            name='organizer',
            field=models.ForeignKey(default=1, to='ezreg.Organizer'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='event',
            name='group',
        ),
        migrations.RemoveField(
            model_name='paymentprocessor',
            name='group',
        ),
        migrations.AlterUniqueTogether(
            name='organizeruserpermission',
            unique_together=set([('organizer', 'user', 'permission')]),
        ),
        migrations.AddField(
            model_name='registration',
            name='test',
            field=models.BooleanField(default=False),
        ),
    ]
