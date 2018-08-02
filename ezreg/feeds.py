from django.contrib.syndication.views import Feed
from django.urls import reverse
from models import Event, Organizer
from django.conf import settings
from django.utils import timezone
    

class EventsFeed(Feed):
#     description_template = 'feeds/beat_description.html'
    description = 'Events'

    def get_object(self, request, organizer_slug):
        return Organizer.objects.get(slug=organizer_slug)

    def title(self, obj):
        return "Upcoming events"

    def item_link(self, item):
        return reverse('event', args=[item.slug_or_id])
    def link(self):
        return getattr(settings,'SITE_URL')
    def item_title(self,item):
        return item.title
    def item_pubdate(self, item):
        return item.start_time
    def item_description(self,item):
        return item.description
    
    def description(self, obj):
        return "Upcoming events for %s"%obj.name

    def items(self, obj):
        return Event.objects.filter(organizer=obj,advertise=True,active=True).order_by('-start_time')

class UpcomingEventsFeed(EventsFeed):
    description = 'Upcoming events'
    def items(self, obj):
        return Event.objects.filter(organizer=obj,start_time__gte=timezone.now(),advertise=True,active=True).order_by('-start_time')

class PastEventsFeed(EventsFeed):
    description = 'Past events'
    def items(self, obj):
        return Event.objects.filter(organizer=obj,start_time__lte=timezone.now(),advertise=True).order_by('-start_time')