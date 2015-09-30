from rest_framework import serializers
from ezreg.models import Price, PaymentProcessor, EventProcessor, EventPage, Registration
from mailqueue.models import MailerMessage

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

class RegistrationSerializer(serializers.ModelSerializer):
    payment__amount = serializers.ReadOnlyField(source='payment.amount')
    payment__processor = serializers.ReadOnlyField(source='payment.processor.name')
    class Meta:
        model = Registration
        fields = ('id','status','event','registered','first_name','last_name','email','institution','department','special_requests','payment__amount','payment__processor')

class MailerMessageSerializer(serializers.ModelSerializer):
#     registrations = serializers.ReadOnlyField(source='registrations',many=True)
#     registrations = serializers.ReadOnlyField(source='registrations')
    registration = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    def get_registration(self, obj):
        registrations = obj.registrations.all()
        return registrations.all()[0].id if registrations.count() else None
    def get_event(self, obj):
        registrations = obj.registrations.all()
        return registrations.all()[0].event_id if registrations.count() else None
    class Meta:
        model = MailerMessage
        fields = ('id','subject','to_address','bcc_address','content','html_content','sent','last_attempt','registration','event')

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