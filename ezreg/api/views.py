from rest_framework import viewsets, status
from ezreg.api.serializers import PriceSerializer, PaymentProcessorSerializer,\
    EventPageSerializer, RegistrationSerializer
from ezreg.models import Price, PaymentProcessor, Event, EventProcessor,\
    EventPage, Registration
from rest_framework.decorators import api_view
from rest_framework.response import Response

# @todo: Secure these for ALL methods (based on price.event.group)!!!
class PriceViewset(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    filter_fields = ('event',)
    search_fields = ('event',)

class PaymentProcessorViewset(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentProcessor.objects.all()
    serializer_class = PaymentProcessorSerializer
    filter_fields = ('group',)
    search_fields = ('group',)
    
class EventPageViewset(viewsets.ModelViewSet):
    queryset = EventPage.objects.all()
    serializer_class = EventPageSerializer
    filter_fields = ('event',)
    search_fields = ('event',)
    
class RegistrationViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
#     filter_fields = ('status','event','email','first_name','last_name')
    filter_fields = {'status':['exact', 'icontains'],'event':['exact'],'email':['exact', 'icontains'],'first_name':['exact', 'icontains'],'last_name':['exact', 'icontains']} 
#     {'name': ['exact', 'icontains'],
#                   'price': ['exact', 'gte', 'lte'],
#                  }
    ordering_fields = ('status','first_name','last_name','email','registered')
    search_fields = ('status','email',)

"""
POST {"processors":{3:{"enabled":true},5:{"enabled":true}}}  where JSON object keys are PaymentProcessor ids
"""
@api_view(['POST','GET'])
def event_payment_processors(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
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
    
    