from django.contrib import admin
from guardian.admin import GuardedModelAdmin

# from django.core.urlresolvers import reverse
from django.utils.html import format_html
from ezreg.models import Event
from ezreg.forms import EventForm
from guardian.shortcuts import get_objects_for_user


class EventAdmin(GuardedModelAdmin):
    model = Event
    form = EventForm
    def get_queryset(self, request):
        return get_objects_for_user(request.user,'view_event',klass=Event)
    def get_form(self, request, obj=None, **kwargs):
#         if request.user.is_superuser:
#             kwargs['form'] = EventForm
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        form.set_user(request.user)
        return form

admin.site.register(Event, EventAdmin)
