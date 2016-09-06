from django.core.management.base import BaseCommand
from ezreg.models import Event

"""
This command can be run periodically with crontab to clear registrations that are beyond their time limit.
For example, to run every 30 minutes:
0,30 * * * * /path/to/python /path/to/manage.py delete_expired_registrations
"""

class Command(BaseCommand):
    help = 'Clear pending registrations that are beyond the time limit'

    def handle(self, *args, **options):
        for event in Event.objects.filter(active=True):
            event.delete_expired_registrations()
        self.stdout.write('Registrations expired')