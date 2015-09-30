from django.shortcuts import render, redirect
from django.template.context import RequestContext
from ezreg.models import Event,  Registration, PaymentProcessor, EventPage
from guardian.shortcuts import get_objects_for_user
from ezreg.forms import EventForm, PaymentProcessorForm,  AdminRegistrationForm,\
    AdminRegistrationStatusForm
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from ezreg.email import  email_status
from django.http.response import HttpResponse
from icalendar import Calendar, Event as CalendarEvent
import json

def home(request):
    return render(request, 'ezreg/home.html', {},context_instance=RequestContext(request))

@login_required
def events(request):
    events = get_objects_for_user(request.user,'view_event',klass=Event)
    return render(request, 'ezreg/events.html', {'events':events},context_instance=RequestContext(request))

@login_required
def create_modify_event(request,id=None):
    instance = None if not id else Event.objects.get(id=id)
#     PriceFormset = formset_factory(PriceForm,extra=4,max_num=10)
#     if instance:
#         PriceFormset = modelformset_factory(Price,exclude=('event',),extra=5)
#     else:
#         PriceFormset = modelformset_factory(Price,exclude=('event',),extra=5)
    
    if request.method == 'GET':
        form = EventForm(request.user,instance=instance)
#         price_formset = PriceFormset(queryset=Price.objects.filter(event=instance))
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST,instance=instance)
#         price_formset = PriceFormset(request.POST)
        if form.is_valid():
            event = form.save()
#             prices = price_formset.save(commit=False)
#             for price in prices:
#                 price.event = event
#                 price.save()
            return redirect('modify_event',id=event.id) #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_event.html', {'form':form,'event':instance} ,context_instance=RequestContext(request))

def event(request,slug_or_id):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    return render(request, 'ezreg/event.html', {'event':event},context_instance=RequestContext(request))

def event_page(request,slug_or_id,page_slug):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    page = EventPage.objects.get(event=event,slug=page_slug)
    return render(request, 'ezreg/page.html', {'event':event,'page':page},context_instance=RequestContext(request))

def registration_ical(request,id):
    registration = Registration.objects.get(id=id)
    event = CalendarEvent()
    event.add('dtstart', registration.event.start_date)
    event.add('summary', registration.event.title)
    response = HttpResponse(event.to_ical(), content_type='text/calendar')
    response['Filename'] = 'event.ics'
    response['Content-Disposition'] = 'inline; filename=event.ics'
    return response

    

@login_required
def modify_registration(request,id=None):
    registration = Registration.objects.get(id=id)
    if request.method == 'GET':
        form = AdminRegistrationForm(instance=registration)
    elif request.method == 'POST':
        form = AdminRegistrationForm(request.POST,instance=registration)
        if form.is_valid():
            registration = form.save()
            return redirect('registrations',slug_or_id=registration.event_id) #event.get_absolute_url()
    return render(request, 'ezreg/modify_registration.html', {'form':form,'registration':registration} ,context_instance=RequestContext(request))

@login_required
def update_registration_status(request,id):
    registration = Registration.objects.get(id=id)
    if request.method == 'GET':
        form = AdminRegistrationStatusForm(instance=registration)
    elif request.method == 'POST':
        form = AdminRegistrationStatusForm(request.POST,instance=registration)
        if form.is_valid():
            registration = form.save()
            email_status(registration,'no-reply@genomecenter.ucdavis.edu')
            return redirect('registrations',slug_or_id=registration.event_id) #event.get_absolute_url()
    return render(request, 'ezreg/update_registration_status.html', {'form':form,'registration':registration} ,context_instance=RequestContext(request))

@login_required
def registrations(request,slug_or_id):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    statuses = json.dumps({status[0]:status[1] for status in Registration.STATUSES})
    processors = json.dumps({processor.name:processor.name for processor in event.payment_processors.all()})
    return render(request, 'ezreg/registrations.html', {'event':event,'Registration':Registration,'statuses':statuses,'processors':processors},context_instance=RequestContext(request))

@login_required
def event_emails(request,slug_or_id):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    return render(request, 'ezreg/event_emails.html', {'event':event},context_instance=RequestContext(request))
# def register(request,id=None):
#     instance = None if not id else Event.objects.get(id=id)
#     if request.method == 'GET':
#         form = EventForm(request.user,instance=instance)
#     elif request.method == 'POST':
#         form = EventForm(request.user,request.POST,instance=instance)
#         if form.is_valid():
#             event = form.save()
#             return redirect('events') #event.get_absolute_url()
#     return render(request, 'ezreg/create_modify_event.html', {'form':form} ,context_instance=RequestContext(request))

def registration(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/registration.html', {'registration':registration},context_instance=RequestContext(request))

def pay(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/pay.html', {'registration':registration},context_instance=RequestContext(request))

@login_required
def payment_processors(request):
    payment_processors = PaymentProcessor.objects.filter(group__in=request.user.groups.all())
    return render(request, 'ezreg/payment_processors.html', {'payment_processors':payment_processors},context_instance=RequestContext(request))




@login_required
def create_modify_payment_processor(request,id=None):
    instance = None if not id else PaymentProcessor.objects.get(id=id)
    if request.method == 'GET':
        form = PaymentProcessorForm(request.user,instance=instance)
    elif request.method == 'POST':
        form = PaymentProcessorForm(request.user,request.POST,instance=instance)
        if form.is_valid():
            processor = form.save()
            return redirect('payment_processors') #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_payment_processor.html', {'form':form} ,context_instance=RequestContext(request))

@login_required
def configure_payment_processor(request,id):
    processor = PaymentProcessor.objects.get(id=id)
    ConfigForm = processor.get_configuration_form()
    if request.method == 'GET':
        form = ConfigForm(initial=processor.config)
    elif request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            processor.config = form.cleaned_data
            processor.save()
            return redirect('payment_processors') #event.get_absolute_url()
    return render(request, 'ezreg/configure_payment_processor.html', {'form':form,'processor':processor} ,context_instance=RequestContext(request))

