from django.core.management.base import BaseCommand
from ezreg.models import Refund
from datetime import timedelta
from django.utils import timezone
# from ezreg.email import generate_email
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
"""
This command can be run daily to alert staff of refund requests.
For example, to run every 30 minutes:
0,30 * * * * /path/to/python /path/to/manage.py refund_request_email
"""

class Command(BaseCommand):
    help = 'Send refund request email'
    def add_arguments(self, parser):
        parser.add_argument('--since_hours', type=int, default=24, help='Include refunds requested in past N hours.')
    def handle(self, *args, **options):
        now = timezone.now()
        since_hours = options.get('since_hours')
        since = now - timedelta(hours=since_hours)
        refunds = Refund.objects.filter(requested__gte=since)
        if refunds.exists():
            html = render_to_string('ezreg/emails/refunds_requested_email.html', {'since': since, 'since_hours': since_hours, 'refunds': refunds})
            send_mail('There are {} new refund requests to be processed'.format(refunds.count()), html, settings.FROM_EMAIL, settings.REFUND_ADMIN_EMAILS, fail_silently=False, html_message=html)
