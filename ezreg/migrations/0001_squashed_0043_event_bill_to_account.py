# Generated by Django 2.2.28 on 2022-05-03 15:11

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_bleach.models
import ezreg.fields
import ezreg.models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    replaces = [('ezreg', '0001_initial'), ('ezreg', '0002_auto_20151013_1452'), ('ezreg', '0003_auto_20151013_1502'), ('ezreg', '0004_auto_20151015_1454'), ('ezreg', '0005_auto_20151015_1704'), ('ezreg', '0006_auto_20151130_1601'), ('ezreg', '0007_auto_20151204_1456'), ('ezreg', '0008_auto_20151207_1010'), ('ezreg', '0009_price_coupon_code'), ('ezreg', '0010_auto_20151208_1519'), ('ezreg', '0011_auto_20160111_1429'), ('ezreg', '0012_event_display_address'), ('ezreg', '0013_auto_20160218_1752'), ('ezreg', '0014_auto_20160801_0858'), ('ezreg', '0015_payment_refunded'), ('ezreg', '0016_auto_20160803_1452'), ('ezreg', '0017_registration_key'), ('ezreg', '0018_auto_20170406_0911'), ('ezreg', '0019_event_logo'), ('ezreg', '0020_auto_20170406_1456'), ('ezreg', '0021_registration_admin_notes'), ('ezreg', '0022_event_outside_url'), ('ezreg', '0023_auto_20170829_1524'), ('ezreg', '0024_auto_20170911_1117'), ('ezreg', '0025_auto_20170914_1455'), ('ezreg', '0026_auto_20180403_1405'), ('ezreg', '0027_auto_20180405_1429'), ('ezreg', '0028_price_quantity'), ('ezreg', '0029_auto_20180618_1643'), ('ezreg', '0030_organizer_config'), ('ezreg', '0031_auto_20180710_1029'), ('ezreg', '0032_auto_20181001_1024'), ('ezreg', '0033_auto_20181108_1038'), ('ezreg', '0034_event_hide_header'), ('ezreg', '0035_event_tentative'), ('ezreg', '0036_auto_20190506_1233'), ('ezreg', '0037_eventpage_index'), ('ezreg', '0038_auto_20200114_1602'), ('ezreg', '0039_auto_20200214_1436'), ('ezreg', '0040_event_department_field'), ('ezreg', '0041_auto_20200605_1330'), ('ezreg', '0042_auto_20200605_1345'), ('ezreg', '0043_event_bill_to_account')]

    initial = True

    dependencies = [
        ('mailqueue', '0002_mailermessage_reply_to'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(default=ezreg.models.id_generator, max_length=10, primary_key=True, serialize=False)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('body', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('cancellation_policy', models.TextField(blank=True, null=True)),
                ('open_until', models.DateField()),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('advertise', models.BooleanField(default=False)),
                ('enable_waitlist', models.BooleanField(default=False)),
                ('enable_application', models.BooleanField(default=False)),
                ('waitlist_message', models.TextField(blank=True, null=True)),
                ('ical', models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files')),
                ('form_fields', jsonfield.fields.JSONField(blank=True, null=True)),
            ],
            options={
                'permissions': (('admin_event', 'Can modify event'), ('view_event', 'Can view event details and registrations')),
            },
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processor_id', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('config', jsonfield.fields.JSONField()),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_processors', to='ezreg.Organizer')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=250)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='ezreg.Event')),
                ('coupon_code', models.CharField(blank=True, max_length=25, null=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('quantity', models.PositiveIntegerField(null=True)),
                ('disable', models.BooleanField(default=False)),
            ],
            options={
                'unique_together': set(),
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.CharField(default=ezreg.models.id_generator, max_length=10, primary_key=True, serialize=False)),
                ('status', models.CharField(blank=True, choices=[(b'REGISTERED', b'Registered'), (b'PENDING_INCOMPLETE', b'Pending'), (b'WAITLIST_PENDING', b'Pending from waitlist'), (b'WAITLISTED', b'Waitlisted'), (b'WAITLIST_INCOMPLETE', b'Waitlist- incomplete'), (b'APPLIED_ACCEPTED', b'Application accepted'), (b'APPLIED_DENIED', b'Application denied'), (b'APPLIED', b'Applied'), (b'APPLY_INCOMPLETE', b'Application- incomplete'), (b'CANCELLED', b'Cancelled')], max_length=25, null=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('test', models.BooleanField(default=False)),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
                ('email_messages', models.ManyToManyField(related_name='registrations', to='mailqueue.MailerMessage')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='ezreg.Event')),
                ('price', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='ezreg.Price')),
                ('registered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('key', models.CharField(default=ezreg.models.id_generator, max_length=10)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'unique_together': set(),
            },
        ),
        migrations.CreateModel(
            name='EventProcessor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ezreg.Event')),
                ('processor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ezreg.PaymentProcessor')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to='ezreg.Organizer'),
        ),
        migrations.AddField(
            model_name='event',
            name='payment_processors',
            field=models.ManyToManyField(through='ezreg.EventProcessor', to='ezreg.PaymentProcessor'),
        ),
        migrations.AddField(
            model_name='event',
            name='bcc',
            field=ezreg.fields.EmailListField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='from_addr',
            field=models.EmailField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='OrganizerUserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[(b'admin', b'Administer'), (b'view', b'View registrations'), (b'manage_processors', b'Manage payment processors')], max_length=25)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='ezreg.Organizer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('organizer', 'user', 'permission')},
            },
        ),
        migrations.AlterField(
            model_name='event',
            name='capacity',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/data/virtualenv/django-ezreg/include/ezreg/files'),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files'),
        ),
        migrations.AddField(
            model_name='event',
            name='expiration_time',
            field=models.PositiveSmallIntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='event',
            name='body',
            field=django_bleach.models.BleachField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='cancellation_policy',
            field=django_bleach.models.BleachField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='event',
            name='display_address',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/data/virtualenv/django-ezreg/include/ezreg/files'),
        ),
        migrations.AddField(
            model_name='event',
            name='contact',
            field=models.TextField(default='UC Davis Bioinformatics Core, bioinformatics.core@ucdavis.edu'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files'),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/data/virtualenv/django-ezreg/include/ezreg/files'),
        ),
        migrations.AddField(
            model_name='event',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=b'logos/'),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files'),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=150),
        ),
        migrations.AddField(
            model_name='event',
            name='outside_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=django_bleach.models.BleachField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/data/virtualenv/django-ezreg/include/ezreg/files'),
        ),
        migrations.AddField(
            model_name='event',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files'),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenv/ezreg/include/ezreg/files'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(b'UNPAID', b'Unpaid'), (b'PENDING', b'Pending'), (b'PAID', b'Paid'), (b'CANCELLED', b'Cancelled'), (b'INVALID_AMOUNT', b'Invalid Amount'), (b'ERROR', b'Error')], default=b'UNPAID', max_length=20)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ezreg.PaymentProcessor')),
                ('registration', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='payment', to='ezreg.Registration')),
                ('external_id', models.CharField(blank=True, max_length=50, null=True)),
                ('refunded', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenvs/django-ezreg/include/ezreg/files'),
        ),
        migrations.AddField(
            model_name='event',
            name='hide_header',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='tentative',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='billed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='ical',
            field=models.FilePathField(blank=True, match=b'*.ics', null=True, path=b'/virtualenv/ezreg/include/ezreg/files'),
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('heading', models.CharField(max_length=40)),
                ('body', django_bleach.models.BleachField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='ezreg.Event')),
                ('index', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('event', 'slug')},
                'ordering': ('index', 'id'),
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('requested', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[(b'pending', b'pending'), (b'cancelled', b'cancelled'), (b'completed', b'completed')], default=b'pending', max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_refunds', to=settings.AUTH_USER_MODEL)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='ezreg.Registration')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_refunds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-requested',),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='department_field',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'permissions': (('admin_event', 'Can modify event'), ('view_event', 'Can view event details and registrations'), ('bill_event', 'Can bill events'))},
        ),
        migrations.AddField(
            model_name='event',
            name='billed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='billed_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='billing_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='bill_to_account',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
