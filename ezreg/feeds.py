from django.contrib.syndication.views import Feed
from django.urls import reverse
from models import Event, Organizer
    

class EventsFeed(Feed):
#     description_template = 'feeds/beat_description.html'
    description = 'Upcoming events'

    def get_object(self, request, organizer_slug):
        return Organizer.objects.get(slug=organizer_slug)

    def title(self, obj):
        return "Upcoming events"

    def item_link(self, item):
        return reverse('event', args=[item.pk])
    
    def item_title(self,item):
        return item.title

    def item_description(self,item):
        return item.description
    
    def description(self, obj):
        return "Upcoming events for %s"%obj.name

    def items(self, obj):
        return Event.objects.filter(organizer=obj).order_by('-start_date')