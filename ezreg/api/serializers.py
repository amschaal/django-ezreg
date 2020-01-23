from rest_framework import serializers
from ezreg.models import Price, PaymentProcessor, EventProcessor, EventPage, Registration,\
    Event, Organizer, Refund
from mailqueue.models import MailerMessage

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class PriceSerializer(serializers.ModelSerializer):
#     coupon_code = serializers.CharField(allow_blank=True, allow_null=True, required=False)
#     def to_internal_value(self, data):
#         if data.has_key('coupon_code'):
#             if not data['coupon_code']: 
#                 data['coupon_code'] = None
#         return super(PriceSerializer,self).to_internal_value(data)
    registration_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Price
        fields = ('id','order','event','name','amount','description','coupon_code','start_date','end_date','quantity', 'registration_count', 'disable')
        extra_kwargs = {'coupon_code': {'required': False,'allow_blank':True,'allow_null':True,'default':None}}

class PaymentProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProcessor
        fields = ('id','processor_id','name','description','hidden')#,'config'
        
class EventPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPage
        fields = ('id','index','event','slug','heading','body')

class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    registered = serializers.ReadOnlyField()
    waitlisted = serializers.ReadOnlyField()
    applied = serializers.ReadOnlyField()
    cancelled = serializers.ReadOnlyField()
    pending = serializers.ReadOnlyField()
    accepted = serializers.ReadOnlyField()
    registration_enabled = serializers.ReadOnlyField()
    organizer = OrganizerSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ('id','organizer','start_time','end_time','title','capacity','registered','waitlisted','applied','accepted','cancelled','pending','registration_enabled','config','billed')

class DetailedEventSerializer(EventSerializer):
    form_fields = serializers.ReadOnlyField()
    class Meta:
        model = Event
        fields = ('id','organizer','start_time','end_time','title','capacity','registered','waitlisted','applied','cancelled','pending','registration_enabled','config','form_fields')

class RegistrationEventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ('id','organizer','title','start_time','end_time')

class RegistrationSerializer(serializers.ModelSerializer):
    payment__amount = serializers.ReadOnlyField(source='payment.amount')
    payment__refunded = serializers.ReadOnlyField(source='payment.refunded')
    payment__processor = serializers.ReadOnlyField(source='payment.processor.name')
    payment__status = serializers.ReadOnlyField(source='payment.status')
    paid = serializers.ReadOnlyField()
    event = RegistrationEventSerializer(read_only=True)
    data = JSONSerializerField()
    class Meta:
        model = Registration
        fields = ('id','status','event','registered','first_name','last_name','email','test','data','payment__amount','payment__processor','payment__status','payment__refunded','paid')

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

class RefundSerializer(serializers.ModelSerializer):
    registrant = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    event_id = serializers.SerializerMethodField()
    external_id = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()
    requester = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    def get_event(self, obj):
        return obj.registration.event.title
    def get_event_id(self, obj):
        return obj.registration.event_id
    def get_external_id(self, obj):
        return getattr(getattr(obj.registration,'payment',None),'external_id',None)
    def get_paid(self, obj):
        return getattr(getattr(obj.registration,'payment',None),'amount',None)
    def get_registrant(self, obj):
        return '{}, {} ({})'.format(obj.registration.last_name,obj.registration.first_name,obj.registration.email)
    def get_admin(self, obj):
        return obj.admin.display() if obj.admin else ''
    def get_requester(self, obj):
        return obj.requester.display() if obj.requester else ''
    class Meta:
        model = Refund
        exclude = []

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
