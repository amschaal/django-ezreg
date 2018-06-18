from rest_framework import viewsets, status
from ezreg.api.serializers import PriceSerializer, PaymentProcessorSerializer,\
    EventPageSerializer, RegistrationSerializer, MailerMessageSerializer,\
    EventSerializer
from ezreg.models import Price, PaymentProcessor, Event, EventProcessor,\
    EventPage, Registration, OrganizerUserPermission
from rest_framework.decorators import api_view, permission_classes, list_route,\
    detail_route
from rest_framework.response import Response
from mailqueue.models import MailerMessage
from ezreg.email import email_status
from ezreg.decorators import event_access_decorator
from django_bleach.utils import get_bleach_default_options
import bleach
from ezreg.utils import format_registration_data
from ezreg.api.permissions import EventPermission
from django.utils import timezone
from django.http.response import HttpResponse
from ezreg.api.filters import MultiFilter
from django_logger.models import Log

# @todo: Secure these for ALL methods (based on price.event.group)!!!
class PriceViewset(viewsets.ModelViewSet):
    serializer_class = PriceSerializer
    filter_fields = ('event',)
    search_fields = ('event',)
    def get_queryset(self):
        return Price.objects.filter(event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN,event__organizer__user_permissions__user=self.request.user)

class PaymentProcessorViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentProcessorSerializer
    filter_fields = ('organizer',)
    search_fields = ('organizer',)
    def get_queryset(self):
        return PaymentProcessor.objects.filter(organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN,organizer__user_permissions__user=self.request.user)

class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
#     filter_fields = ('event',)
    filter_fields = {'title':[ 'icontains'],'organizer__name':['icontains'],'active':['exact']}
    search_fields = ('title',)
    ordering_fields = ('start_time','title','organizer__name')
    permission_classes = (EventPermission,)
    def get_queryset(self):
        return Event.objects.filter(organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_VIEW,organizer__user_permissions__user=self.request.user)
#     @detail_route(methods=['GET'])
#     def get_config(self,request,*args,**kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)

class EventPageViewset(viewsets.ModelViewSet):
    serializer_class = EventPageSerializer
    filter_fields = ('event',)
    search_fields = ('event',)
    def get_queryset(self):
        return EventPage.objects.filter(event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN,event__organizer__user_permissions__user=self.request.user)

class RegistrationViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationSerializer
    filter_backends = viewsets.ReadOnlyModelViewSet.filter_backends + [MultiFilter]
#     filter_fields = ('status','event','email','first_name','last_name')
    multi_filters = ['status__in','payment__status__in']
    filter_fields = {'status':['exact', 'icontains'],'registered':['gte','lte'],'event':['exact'],'event__title':['icontains'],'event__organizer__name':['icontains'],'email':['exact', 'icontains'],'first_name':['exact', 'icontains'],'last_name':['exact', 'icontains'],'payment__processor__name':['exact'],'payment__status':['exact'],'test':['exact']} 
#     {'name': ['exact', 'icontains'],
#                   'price': ['exact', 'gte', 'lte'],
#                  }
    ordering_fields = ('status','first_name','last_name','email','registered','payment__amount','payment__status','payment__processor__name','event__title','event__organizer__name')
    search_fields = ('status','email',)
    def get_queryset(self):
        print self.request.query_params
        return Registration.objects.filter(event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_VIEW,event__organizer__user_permissions__user=self.request.user)
    @list_route()
    def export_registrations(self,request):
        import tablib
        registrations = self.filter_queryset(self.get_queryset())
        fields = ['registered','event_id','event','organizer','first_name','last_name','email','amount','refunded','processor','status','payment status','admin_notes','test']
        
        #add headers
        dataset = tablib.Dataset(headers=fields)
        
        #write data
        for r in registrations:
            amount = None if not hasattr(r,'payment') else r.payment.amount
            refunded = None if not hasattr(r,'payment') else r.payment.refunded
            processor = None if not hasattr(r,'payment') or not r.payment.processor else r.payment.processor.name
            payment_status = None if not hasattr(r,'payment') else r.payment.status
            dataset.append([r.registered.strftime("%Y-%m-%d %H:%M"),r.event.id,r.event.title,r.event.organizer.name,r.first_name,r.last_name,r.email,amount,refunded,processor,r.status,payment_status,r.admin_notes,r.test])
        filetype = request.query_params.get('export_format','xls')
        filetype = filetype if filetype in ['xls','xlsx','csv','tsv','json'] else 'xls'
        content_types = {'xls':'application/vnd.ms-excel','tsv':'text/tsv','csv':'text/csv','json':'text/json','xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        response_kwargs = {
                'content_type': content_types[filetype]
            }
        filename = "registrations_%s.%s"%(timezone.now().strftime("%Y_%m_%d__%H_%M"),filetype)
        response = HttpResponse(getattr(dataset, filetype), **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response

class MailerMessageViewset(viewsets.ReadOnlyModelViewSet):
#     queryset = MailerMessage.objects.all().prefetch_related('registrations')
    serializer_class = MailerMessageSerializer
    filter_fields = {'registrations__id':['exact'],'registrations__event':['exact'],'sent':['exact'],'to_address':['exact','icontains'],'bcc_address':['exact','icontains'],'subject':['exact','icontains']}
    search_fields = ('to_address',)
    def get_queryset(self):
        return MailerMessage.objects.filter(registrations__event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_VIEW,registrations__event__organizer__user_permissions__user=self.request.user).prefetch_related('registrations')
"""
POST {"processors":{3:{"enabled":true},5:{"enabled":true}}}  where JSON object keys are PaymentProcessor ids
"""

@api_view(['POST','GET'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def event_payment_processors(request, event):
    try:
        if request.method == 'POST':
            processors = request.data.get('processors')
            EventProcessor.objects.filter(event=event).delete()
            for id, processor in processors.iteritems():
                print id
                print processor
                if processor['enabled']:
                    EventProcessor.objects.create(processor_id=id,event=event)
        event_processors = EventProcessor.objects.filter(event=event)
        return Response({'processors':{p.processor_id:{'enabled':True} for p in event_processors}})
    except Exception, e:
        return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
#         EventProcessor.objects.
#     payment_processors = PaymentProcessor.objects.filter(group=event.group)
#     EventProcessor.objects.filter(event=event).delete()
#     for processor in processors:
#         EventProcessor.objects.create(event=event,processor_id=processor['id'])

@api_view(['POST'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def update_event_statuses(request, event):
    registrations = event.registrations.filter(id__in=request.data.get('selected'))
    registrations.update(status=request.data.get('status'))
    for registration in registrations:
        Log.create(text='Registration status for %s updated to %s by %s'%(registration.email,registration.status,request.user.username),objects=[registration,registration.event,request.user])
        if request.data.get('send_email'):
            email_status(registration)
    return Response({'status':'success'})



@api_view(['POST'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def update_event_form(request, event):
    if request.data.get('form_fields'):
        event.form_fields = request.data.get('form_fields')
        for i, field in enumerate(event.form_fields):
            if field.has_key('html'):
                event.form_fields[i]['html'] = bleach.clean(event.form_fields[i]['html'], **get_bleach_default_options())#removetags(event.form_fields[i]['html'], 'script style')
        event.save()
    return Response({'status':'success'})

@api_view(['POST'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def send_event_emails(request, event):
    emails = MailerMessage.objects.filter(registrations__event_id=event.id,id__in=request.data.get('selected'))
    for email in emails:
        email.send_mail()
    return Response({'status':'success'})

@api_view(['GET'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_VIEW])
def export_registrations(request, event):
    selection = request.POST.getlist('selection',None)
    if selection:
        registrations = event.registrations.filter(id__in=request.POST.getlist('selection')).prefetch_related('payment','payment__processor')
    else:
        registrations = event.registrations.all().prefetch_related('payment','payment__processor')
    data = format_registration_data(event, registrations)
    return Response(data)
    