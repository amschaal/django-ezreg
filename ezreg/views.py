from django.shortcuts import render, redirect
from django.template.context import RequestContext
from ezreg.models import Event,  Registration, PaymentProcessor, EventPage,\
    id_generator, EventProcessor, OrganizerUserPermission
from guardian.shortcuts import get_objects_for_user
from ezreg.forms import EventForm, PaymentProcessorForm,  AdminRegistrationForm,\
    AdminRegistrationStatusForm
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from ezreg.email import  email_status
from django.http.response import HttpResponse
from icalendar import Calendar, Event as CalendarEvent
from datetime import datetime
import json
import csv
from ezreg.decorators import event_access_decorator

def home(request):
    upcoming = Event.objects.filter(advertise=True,active=True,open_until__gte=datetime.today()).order_by('start_time')[:5]
    return render(request, 'ezreg/home.html', {'upcoming':upcoming},context_instance=RequestContext(request))

@login_required
def events(request):
    events = get_objects_for_user(request.user,'view_event',klass=Event)
    return render(request, 'ezreg/events.html', {'events':events},context_instance=RequestContext(request))

@login_required
def create_event(request):
    if request.method == 'GET':
        form = EventForm(request.user)
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST)
        if form.is_valid():
            event = form.save()
            return redirect('manage_event',id=event.id) #event.get_absolute_url()
    return render(request, 'ezreg/create_event.html', {'form':form} ,context_instance=RequestContext(request))


@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def delete_event(request,event):
    event.delete()
    return redirect('events')

@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def copy_event(request,event):
    copied = Event.objects.get(id=event.id)
    event.pk = id_generator() #this will make copy on save
    event.id = id_generator()
#     event.pk = 
    if event.slug:
        event.slug = 'copy_of_'+event.slug
    event.title = 'Copy of '+event.title
    event.save()
    for processor in copied.payment_processors.all():
        EventProcessor.objects.create(event=event,processor=processor)
#     event.save()
#     for page in copied.pages.all():
#         EventPage.objects.create(event=event,slug=page.slug,heading=page.heading,body=page.body)
    for page in copied.pages.all():
        page.pk = None
        page.event = event
        page.save()
    for price in copied.prices.all():
        price.pk = None
        price.event = event
        price.save()
    return redirect('manage_event',event=event.id)

@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN,OrganizerUserPermission.PERMISSION_VIEW],require_all=False)
def manage_event(request,event):
    statuses = json.dumps({status[0]:status[1] for status in Registration.STATUSES})
    processors = json.dumps({processor.name:processor.name for processor in event.payment_processors.all()})
    form_fields = json.dumps(event.form_fields) if event.form_fields else '[]'
    if request.method == 'GET':
        form = EventForm(request.user,instance=event)
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST,instance=event)
        if form.is_valid():
            event = form.save()
            return redirect('manage_event',event=event.id) #event.get_absolute_url()
    return render(request, 'ezreg/event/manage.html', {'form':form,'event':event,'Registration':Registration,'statuses':statuses,'processors':processors,'form_fields':form_fields} ,context_instance=RequestContext(request))
    

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


def registration(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/registration.html', {'registration':registration},context_instance=RequestContext(request))

def pay(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/pay.html', {'registration':registration},context_instance=RequestContext(request))

@login_required
def payment_processors(request):
    OUPs = OrganizerUserPermission.objects.filter(user=request.user,permission=OrganizerUserPermission.PERMISSION_ADMIN)
    payment_processors = PaymentProcessor.objects.filter(organizer_id__in=[oup.organizer_id for oup in OUPs])
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

    
@event_access_decorator([OrganizerUserPermission.PERMISSION_VIEW])
def export_registrations(request, event):
    print request.POST.getlist('selection')
    registrations = event.registrations.filter(email__in=request.POST.getlist('selection'))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    print request.POST
    form_fields = [field for field in event.form_fields if 'layout' not in field['type'] and request.POST.get('fields_%s'%field['name'],False)]
    fields = ['First Name', 'Last Name', 'Email']
    fields += [field['label'] for field in form_fields]
    
    writer.writerow(fields)
    for r in registrations:
        values = [r.first_name, r.last_name, r.email]
        values += [r.get_form_value(field['name']) for field in form_fields]
        writer.writerow(values)

    return response