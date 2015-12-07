from rest_framework import viewsets, status
from ezreg.api.serializers import PriceSerializer, PaymentProcessorSerializer,\
    EventPageSerializer, RegistrationSerializer, MailerMessageSerializer
from ezreg.models import Price, PaymentProcessor, Event, EventProcessor,\
    EventPage, Registration, OrganizerUserPermission
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mailqueue.models import MailerMessage
from ezreg.email import email_status
from ezreg.decorators import event_access_decorator

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
    
class EventPageViewset(viewsets.ModelViewSet):
    serializer_class = EventPageSerializer
    filter_fields = ('event',)
    search_fields = ('event',)
    def get_queryset(self):
        return EventPage.objects.filter(event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN,event__organizer__user_permissions__user=self.request.user)
    
class RegistrationViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationSerializer
#     filter_fields = ('status','event','email','first_name','last_name')
    filter_fields = {'status':['exact', 'icontains'],'event':['exact'],'email':['exact', 'icontains'],'first_name':['exact', 'icontains'],'last_name':['exact', 'icontains'],'payment__processor__name':['exact'],'payment__status':['exact'],'test':['exact']} 
#     {'name': ['exact', 'icontains'],
#                   'price': ['exact', 'gte', 'lte'],
#                  }
    ordering_fields = ('status','first_name','last_name','email','registered','payment__amount','payment__status')
    search_fields = ('status','email',)
    def get_queryset(self):
        return Registration.objects.filter(event__organizer__user_permissions__permission=OrganizerUserPermission.PERMISSION_VIEW,event__organizer__user_permissions__user=self.request.user)

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
    registrations = event.registrations.filter(email__in=request.data.get('selected'))
    registrations.update(status=request.data.get('status'))
    if request.data.get('send_email'):
        for registration in registrations:
            email_status(registration)
    return Response({'status':'success'})

@api_view(['POST'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def update_event_form(request, event):
    if request.data.get('form_fields'):
        event.form_fields = request.data.get('form_fields') 
        event.save()
    return Response({'status':'success'})

@api_view(['POST'])
@event_access_decorator([OrganizerUserPermission.PERMISSION_ADMIN])
def send_event_emails(request, event):
    emails = MailerMessage.objects.filter(registrations__event_id=event.id,id__in=request.data.get('selected'))
    for email in emails:
        email.send_mail()
    return Response({'status':'success'})

    