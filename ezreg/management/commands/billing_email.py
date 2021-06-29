from django.core.management.base import BaseCommand
from ezreg.models import Event, Organizer, OrganizerUserPermission
from datetime import timedelta
from django.utils import timezone
# from ezreg.email import generate_email
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
"""
This command can be run periodically with crontab to send billing emails.
For example, to run every 30 minutes:
0,30 * * * * /path/to/python /path/to/manage.py billing_email
"""

class Command(BaseCommand):
    help = 'Send billing reminder email'

    def handle(self, *args, **options):
        today = timezone.now()
        period_start = today - timedelta(weeks=4*80)
        period_end = today - timedelta(weeks=4)
        for o in Organizer.objects.all():
            billable = []
            admins = [oup.user for oup in OrganizerUserPermission.objects.filter(organizer=o, permission=OrganizerUserPermission.PERMISSION_ADMIN)]
            total = 0
            for e in Event.objects.filter(end_time__gte=period_start, end_time__lte=period_end, billed=False, organizer=o).order_by('start_time'):
                bill = e.revenue > 0
    #             self.stdout.write('event: {}'.format(event.title))
                if not bill:
                    print('FREE')
                else:
                    billable.append(e)
                    total += e.total_charges
            if len(billable) > 0:
#                 print('Organizer', o, billable)
                html = render_to_string('ezreg/emails/billing_email.html', {'start': period_start, 'end': period_end, 'organizer': o, 'admins': admins, 'events': billable, 'SITE_URL': settings.SITE_URL, 'total': total})
                send_mail('Registration system billing for {}'.format(o), html, settings.FROM_EMAIL, ['amschaal@ucdavis.edu'], fail_silently=False, html_message=html)
#             send_email('amschaal@ucdavis.edu', settings.FROM_EMAIL, 'Registration system billing for {}'.format(o), template, html_template, context, cc, bcc, registration)
#             generate_email('amschaal@ucdavis.edu', settings.FROM_EMAIL, 'Registration system billing for {}'.format(o), , 'ezreg/emails/billing_email.html', { 'organizer': o, 'events': billable})
#         self.stdout.write('Registrations expired')