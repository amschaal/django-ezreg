from django.shortcuts import render, redirect
from ezreg.models import Event,  Registration, PaymentProcessor, EventPage,\
    id_generator, EventProcessor, OrganizerUserPermission, Payment, Organizer,\
    Refund
from ezreg.forms import EventForm, PaymentProcessorForm,  AdminRegistrationForm,\
    AdminRegistrationStatusForm, PriceForm, AdminPriceForm, AdminPaymentForm,\
    RefundRequestForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query_utils import Q
from ezreg.email import  email_status
from django.http.response import HttpResponse
from icalendar import Calendar, Event as CalendarEvent
from datetime import datetime
import json
import csv
from ezreg.decorators import event_access_decorator,\
    generic_permission_decorator, has_permissions
from django_json_forms.forms import JSONForm
from django.utils import timezone
from collections import OrderedDict
from ezreg.utils import format_registration_data
from ezreg.templatetags.ezreg_filters import form_value
from ezreg.custom_texts import CUSTOM_TEXTS
from django.db.models.aggregates import Sum
from decimal import Decimal
from django_logger.models import Log
from django.http import Http404

def home(request, organizer_slug=None):
    organizer = Organizer.objects.filter(slug=organizer_slug).first()
    organizers = Organizer.objects.all().order_by('name')
    if organizer:
        upcoming = Event.objects.filter(advertise=True,start_time__gte=datetime.today(),organizer=organizer).order_by('start_time')
        past= Event.objects.filter(advertise=True,start_time__lt=datetime.today(),organizer=organizer).order_by('-start_time')
    else:
        upcoming = Event.objects.filter(advertise=True,start_time__gte=datetime.today()).order_by('start_time')
        past = Event.objects.filter(advertise=True,start_time__lt=datetime.today()).order_by('-start_time')[:5]
    return render(request, 'ezreg/home.html', {'upcoming':upcoming,'past':past,'organizer':organizer, 'organizers': organizers})

def events(request,page='upcoming'):
    if page == 'past':
        events = Event.objects.filter(advertise=True,open_until__lt=datetime.today()).order_by('-start_time')
        template = 'ezreg/partials/past_events.html'
    else:
        events = Event.objects.filter(advertise=True,open_until__gte=datetime.today()).order_by('start_time')
        template = 'ezreg/partials/upcoming_events.html'
    return render(request, 'ezreg/events.html', {'events':events,'template':template})

@has_permissions([OrganizerUserPermission.PERMISSION_ADMIN,OrganizerUserPermission.PERMISSION_VIEW],require_all=False)
def manage_events(request):
#     events = Event.objects.filter(organizer__user_permissions__user=request.user).distinct()
    return render(request, 'ezreg/manage_events.html')

@has_permissions([OrganizerUserPermission.PERMISSION_ADMIN,OrganizerUserPermission.PERMISSION_VIEW],require_all=False)
def registration_search(request):
    statuses = json.dumps({status[0]:status[1] for status in Registration.STATUSES})
    payment_statuses = json.dumps({status[0]:status[1] for status in Payment.STATUS_CHOICES})
    return render(request, 'ezreg/registration_search.html', {'statuses':statuses,'payment_statuses':payment_statuses})

@has_permissions([OrganizerUserPermission.PERMISSION_ADMIN])
def create_event(request):
    if request.method == 'GET':
        form = EventForm(request.user)
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST)
        if form.is_valid():
            event = form.save()
            return redirect('manage_event',event=event.id) #event.get_absolute_url()
    return render(request, 'ezreg/create_event.html', {'form':form} )


@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def delete_event(request,event):
    if event.registrations.exclude(test=True).count() > 0:
        return render(request, 'ezreg/message.html', {'message':'Events with registrations may not be deleted.'} )
    event.delete()
    return redirect('manage_events')

@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def copy_event(request,event):
    copied = Event.objects.get(id=event.id)
    event.pk = id_generator() #this will make copy on save
    event.id = id_generator()
    tstamp = timezone.now().strftime("%Y_%m_%d__%H_%M")
    event.slug = 'copy_of_%s_%s'%(event.slug,tstamp)
    event.title = 'Copy of %s %s'%(event.title,tstamp)
    event.active = event.advertise = event.billed = False
    event.billed_on = None
    event.billed_by = None
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
    if request.method == 'GET':
        form = EventForm(request.user,instance=event)
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST,request.FILES,instance=event)
        if form.is_valid():
            event = form.save()
#             return redirect('manage_event',event=event.id) #event.get_absolute_url()
    statuses = json.dumps({status[0]:status[1] for status in Registration.STATUSES})
    payment_statuses = json.dumps({status[0]:status[1] for status in Payment.STATUS_CHOICES})
    processors = json.dumps({processor.name:processor.name for processor in event.payment_processors.all()})
    form_fields = json.dumps(event.form_fields) if event.form_fields else '[]'
    permissions = event.get_user_permissions(request.user)
    refunds = Refund.objects.filter(registration__event=event)
    return render(request, 'ezreg/event/manage.html', {'form':form,'event':event,'Registration':Registration,'statuses':statuses,'payment_statuses':payment_statuses,'processors':processors,'form_fields':form_fields,'permissions':permissions,'custom_texts':json.dumps(CUSTOM_TEXTS), 'refunds': refunds} )
    

def event(request,slug_or_id):
    try:
        event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    except Event.DoesNotExist as e:
        raise Http404('Event not found')
    return render(request, 'ezreg/event.html', {'event':event})

def event_page(request,slug_or_id,page_slug):
    try:
        event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
        page = EventPage.objects.get(event=event,slug=page_slug)
    except:
        raise Http404('Event or event page not found')
    return render(request, 'ezreg/page.html', {'event':event,'page':page})


@generic_permission_decorator([OrganizerUserPermission.PERMISSION_ADMIN],'organizer__events__registrations__id','id')
def modify_registration(request,id=None):
    registration = Registration.objects.get(id=id)
    fields = registration.event.form_fields if isinstance(registration.event.form_fields,list) else None
    extra_fields_form = None
    if request.method == 'GET':
        form = AdminRegistrationForm(instance=registration)
        if fields:
            extra_fields_form = JSONForm(registration.data,fields=fields)  
    elif request.method == 'POST':
        form = AdminRegistrationForm(request.POST,instance=registration)
        if fields:
            extra_fields_form = JSONForm(request.POST,fields=fields)  
        if form.is_valid() and (not extra_fields_form or extra_fields_form.is_valid()):
            registration = form.save()
            if extra_fields_form:
                registration.data = extra_fields_form.cleaned_data
                registration.save()
            Log.create(text='Registration for %s (%s) updated by %s.'%(registration.email, registration.id,request.user.username),objects=[registration,registration.event,request.user])
            return redirect('manage_event',event=registration.event_id) #event.get_absolute_url()
    return render(request, 'ezreg/modify_registration.html', {'form':form,'registration':registration,'extra_fields_form':extra_fields_form} )

@generic_permission_decorator([OrganizerUserPermission.PERMISSION_ADMIN],'organizer__events__registrations__id','id')
def modify_payment(request,id=None):
    registration = Registration.objects.get(id=id)
    payment = registration.get_payment()
    PAID = getattr(payment, 'status') == Payment.STATUS_PAID
    form_class = payment.get_form()
    if request.method == 'GET':
        price_form = None if PAID else AdminPriceForm({'price':registration.price_id},event=registration.event)
        payment_form = form_class(payment.data,event=registration.event) if form_class else None
        admin_payment_form = AdminPaymentForm(instance=payment,prefix="admin_payment_form")
    elif request.method == 'POST':
        payment_form = form_class(request.POST,event=registration.event) if form_class else None
        old_payment_status = payment.status
        admin_payment_form = AdminPaymentForm(request.POST,instance=payment,prefix="admin_payment_form")
        price_form = None if PAID else AdminPriceForm(request.POST,event=registration.event)
        if (PAID or price_form.is_valid()) and admin_payment_form.is_valid() and (payment_form is None or payment_form.is_valid()):
            payment = admin_payment_form.save(commit=False)
            if payment_form:
                payment.data = payment_form.cleaned_data
            if not PAID:
                registration.price = price_form.cleaned_data['price']
                payment.amount = price_form.cleaned_data['price'].amount
            payment.save()
            registration.save()
            if old_payment_status != admin_payment_form.cleaned_data['status']:
                Log.create(text='Payment status for %s (%s) updated by %s: %s -> %s.'%(registration.email, registration.id, request.user.username, old_payment_status, admin_payment_form.cleaned_data['status']),objects=[registration,registration.event,request.user])
            Log.create(text='Payment for %s (%s) updated by %s.  Price: %s, Refund: %s.'%(registration.email, registration.id, request.user.username, payment.amount, payment.refunded),objects=[registration,registration.event,request.user])
            return render(request, 'ezreg/modify_payment.html', {'payment_form':payment_form,'admin_payment_form':admin_payment_form,'price_form':price_form,'registration':registration,'payment':payment} )
    return render(request, 'ezreg/modify_payment.html', {'payment_form':payment_form,'price_form':price_form,'admin_payment_form':admin_payment_form,'registration':registration,'payment':payment} )

@generic_permission_decorator([OrganizerUserPermission.PERMISSION_ADMIN],'organizer__events__registrations__id','id')
def update_registration_status(request,id):
    registration = Registration.objects.get(id=id)
    if request.method == 'GET':
        form = AdminRegistrationStatusForm(instance=registration)
    elif request.method == 'POST':
        form = AdminRegistrationStatusForm(request.POST,instance=registration)
        if form.is_valid():
            registration = form.save()
            email_status(registration)
            Log.create(text='Registration status for %s updated to %s by %s'%(registration.email,registration.status,request.user.username),objects=[registration,registration.event,request.user])
            return redirect('registrations',slug_or_id=registration.event_id) #event.get_absolute_url()
    return render(request, 'ezreg/update_registration_status.html', {'form':form,'registration':registration} )

@generic_permission_decorator([OrganizerUserPermission.PERMISSION_ADMIN],'organizer__events__registrations__id','id')
def request_refund(request, id):
    registration = Registration.objects.get(id=id)
    if request.method == 'GET':
        form = RefundRequestForm(user=request.user, registration=registration)
    elif request.method == 'POST':
        form = RefundRequestForm(request.POST, user=request.user, registration=registration)
        if form.is_valid():
            refund = form.save()
            # @todo: Email admins here?
            Log.create(text='Refund request for %s created %s by %s'%(registration.email,refund.requested,request.user.username),objects=[registration,registration.event,request.user])
            return redirect('registration',id=registration.id) #event.get_absolute_url()
    return render(request, 'ezreg/request_refund.html', {'form':form,'registration':registration} )

@user_passes_test(lambda u: u.is_staff)
def pending_refunds(request):
    return render(request, 'ezreg/admin/pending_refunds.html', {})

def registration(request,id):
    try:
        registration = Registration.objects.get(id=id)
    except Registration.DoesNotExist:
        raise Http404('Registration not found')
    permissions = registration.event.get_user_permissions(request.user) if request.user.is_authenticated else []
    return render(request, 'ezreg/registration.html', {'registration':registration, 'permissions': permissions})

def cancel_registration(request,id):
    key = request.GET.get('key',None)
    registration = Registration.objects.get(id=id,key=key)
    if registration.status in [Registration.STATUS_WAITLIST_PENDING,Registration.STATUS_WAITLISTED]:
        registration.status = Registration.STATUS_CANCELLED
        registration.save()
        email_status(registration)
        message = 'Your registration has been cancelled'
        Log.create(text='Registration for %s cancelled'%(registration.email),objects=[registration])
    else:
        message = 'Registration can only be cancelled if you are currently waitlisted'
    return render(request, 'ezreg/registration.html', {'registration':registration,'message':message})

def pay(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, registration.payment.processor.get_processor().payment_template, {'registration':registration})

@has_permissions([OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS])
def payment_processors(request):
    payment_processors = PaymentProcessor.get_user_queryset(user=request.user).order_by('organizer__name','processor_id','name')
    return render(request, 'ezreg/payment_processors.html', {'payment_processors':payment_processors})


@generic_permission_decorator([OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS],'organizer__payment_processors__id','id')
def modify_payment_processor(request,id):
    instance = PaymentProcessor.objects.get(id=id)
    if request.method == 'GET':
        form = PaymentProcessorForm(request.user,instance=instance)
    elif request.method == 'POST':
        form = PaymentProcessorForm(request.user,request.POST,instance=instance)
        if form.is_valid():
            processor = form.save()
            Log.create(text='Payment processor updated by %s'%(request.user.username),objects=[request.user,processor])
            return redirect('configure_payment_processor',id=processor.id) #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_payment_processor.html', {'form':form} )

@has_permissions([OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS])
def create_payment_processor(request):
    if request.method == 'GET':
        form = PaymentProcessorForm(request.user)
    elif request.method == 'POST':
        form = PaymentProcessorForm(request.user,request.POST)
        if form.is_valid():
            processor = form.save()
            Log.create(text='Payment processor created by %s'%(request.user.username),objects=[request.user,processor])
            return redirect('configure_payment_processor',id=processor.id) #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_payment_processor.html', {'form':form} )

@generic_permission_decorator([OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS],'organizer__payment_processors__id','id')
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
            Log.create(text='Payment processor configured by %s'%(request.user.username),objects=[request.user,processor])
            return redirect('payment_processors') #event.get_absolute_url()
    return render(request, 'ezreg/configure_payment_processor.html', {'form':form,'processor':processor} )


#@todo: Pretty ugly.  Should modularize this.  Handling custom payment data, custom form data, etc should be abstracted out of this function.
@event_access_decorator([OrganizerUserPermission.PERMISSION_VIEW])
def export_registrations_old(request, event):
    import re
#     print request.POST.getlist('selection')
    registrations = event.registrations.filter(id__in=request.POST.getlist('selection')).prefetch_related('payment','payment__processor')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_registrations_%s.csv"'%(re.sub('[^0-9a-zA-Z_]+', '', event.title.replace(' ','_')) ,timezone.now().strftime("%Y_%m_%d__%H_%M"))
    writer = csv.writer(response)
    form_fields = []
    if event.form_fields:
        form_fields = [field for field in event.form_fields if 'layout' not in field['type'] and field['name'] in request.POST.getlist('custom_fields')]
    fields = ['Registered','First Name', 'Last Name', 'Email','Status']
    fields += [field['label'] for field in form_fields]
    
    payment_fields_all = OrderedDict([('processor','Processor'),('status','Payment Status'),('paid_at','Paid at'),('amount','Amount'),('external_id','External ID')])
    payment_fields = OrderedDict([(key,payment_fields_all[key]) for key in request.POST.getlist('payment_fields') if key in payment_fields_all])
    
    fields += payment_fields.values()
    
    processor_fields = OrderedDict()
    processor_field_labels = []
    for processor in event.payment_processors.all():
        proc_fields = request.POST.getlist('processor_%d'%processor.id)
        if len(proc_fields):
            exportable_fields = processor.get_processor().exportable_fields
            processor_fields[processor.id]=proc_fields
            processor_field_labels += [exportable_fields[field] for field in proc_fields]
    fields += processor_field_labels
    
    writer.writerow(fields)
    
    for r in registrations:
        values = [r.registered, r.first_name, r.last_name, r.email, r.status]
        #Add custom form field values
        values += [r.get_form_value(field['name']) for field in form_fields]
        
        
        payment = r.get_payment()
        
        #Add selected payment fields
        if payment:
            values += [getattr(payment, key) for key in payment_fields.keys()]
        else:
            values += ['' for key in payment_fields.keys()]
        
        #Add selected payment processor fields
        for processor_id, fields in processor_fields.iteritems():
            for field in fields:
                if payment:
                    if payment.processor_id == processor_id and payment.data:
                        values.append(payment.data.get(field,''))
                        continue
                values.append('')
                
        unicode_values = [unicode(v).encode("utf-8") for v in values]
        writer.writerow(unicode_values)

    return response


@event_access_decorator([OrganizerUserPermission.PERMISSION_VIEW])
def export_registrations(request, event):
    import re, tablib
    registrations = event.registrations.filter(id__in=request.POST.getlist('selection')).prefetch_related('payment','payment__processor').order_by('registered')
    data = format_registration_data(event, registrations)
    fields = ['registered','id','first_name','last_name','email', 'department','admin_notes','status']
    if event.form_fields:
        fields += [field['name'] for field in event.form_fields if 'layout' not in field['type'] and field['name'] in request.POST.getlist('custom_fields')]
    fields += request.POST.getlist('payment_fields')
    for processor in event.payment_processors.all():
        fields += request.POST.getlist('processor_%d'%processor.id)
    
    #get rid of fields that aren't available
    fields = [field for field in fields if field in data['fields']]
    
    #add headers
    dataset = tablib.Dataset(headers=[data['fields'][field].get('label',field) for field in fields])
    
    #write data
    for row in data['data']:
        dataset.append([form_value(row.get(field,'')) for field in fields])

    filetype = request.POST.get('format','xls')
    filetype = filetype if filetype in ['xls','xlsx','csv','tsv','json'] else 'xls'
    content_types = {'xls':'application/vnd.ms-excel','csv':'text/csv','tsv':'text/tsv','json':'text/json','xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
    response_kwargs = {
            'content_type': content_types[filetype]
        }
    filename = "%s_registrations_%s.%s"%(re.sub('[^0-9a-zA-Z_]+', '', event.title.replace(' ','_')) ,timezone.now().strftime("%Y_%m_%d__%H_%M"),filetype)
    response = HttpResponse(getattr(dataset, filetype), **response_kwargs)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@has_permissions([OrganizerUserPermission.PERMISSION_ADMIN,OrganizerUserPermission.PERMISSION_VIEW],require_all=False)
def export_event_revenue(request):
    import re, tablib
    dataset = dataset = tablib.Dataset(headers=['closing date','event','organizer','registered revenue','registered refunds','registered total','all revenue','all refunds','all total'])
    qs = Event.objects.all() if request.user.is_staff else Event.objects(organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_VIEW,organizer__user_permissions__user=request.user)
    for e in qs.order_by('organizer__name','-end_time'):
        all_revenue = Payment.objects.filter(registration__event=e,registration__test=False).aggregate(Sum('amount'),Sum('refunded'))
        registered_revenue = Payment.objects.filter(registration__status=Registration.STATUS_REGISTERED,registration__event=e,registration__test=False).aggregate(Sum('amount'),Sum('refunded'))
        all_total = (all_revenue['amount__sum'] if all_revenue['amount__sum'] else Decimal(0.0))-(all_revenue['refunded__sum'] if all_revenue['refunded__sum'] else Decimal(0.0))
        registered_total = (registered_revenue['amount__sum']if registered_revenue['amount__sum'] else Decimal(0.0))-(registered_revenue['refunded__sum'] if registered_revenue['refunded__sum'] else Decimal(0.0))
        dataset.append([e.open_until.strftime("%Y_%m_%d"),e.title,e.organizer.name,registered_revenue['amount__sum'],registered_revenue['refunded__sum'],registered_total,all_revenue['amount__sum'],all_revenue['refunded__sum'],all_total])
    filetype = request.POST.get('format','xls')
    filetype = filetype if filetype in ['xls','xlsx','csv','tsv','json'] else 'xls'
    content_types = {'xls':'application/vnd.ms-excel','csv':'text/csv','json':'text/json','xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
    response_kwargs = {
            'content_type': content_types[filetype]
        }
    filename = "event_revenue_%s.%s"%(timezone.now().strftime("%Y_%m_%d__%H_%M"),filetype)
    response = HttpResponse(dataset.export(filetype), **response_kwargs)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
