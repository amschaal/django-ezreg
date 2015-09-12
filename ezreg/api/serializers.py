from rest_framework import serializers
from ezreg.models import Price, PaymentProcessor, EventProcessor, EventPage

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('id','event','name','amount','description','start_date','end_date')

class PaymentProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProcessor
        fields = ('id','processor_id','group','name','description','hidden','config')
        
class EventPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPage
        fields = ('id','event','slug','heading','body')

# class EventProcessorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EventProcessor
#         fields = ('id','processor_id','group','name','description','hidden','config')

# class ProjectSerializer(serializers.ModelSerializer):
#     lab__name = serializers.Field(source='lab.name')
#     type = serializers.RelatedField(many=False)
#     data = JSONWritableField()
#     class Meta:
#         model = Project
#         fields = ('id','name','type','description','lab','lab__name','data')