from rest_framework import viewsets
from ezreg.api.serializers import PriceSerializer
from ezreg.models import Price
from rest_framework.decorators import api_view

# @todo: Secure these for ALL methods (based on price.event.group)!!!
class PriceViewset(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    filter_fields = ('event',)


#     search_fields = (, 'job_id','script_path','status')
#     ordering_fields = ('created','run','status')
#     ordering = ('-amount',)
    