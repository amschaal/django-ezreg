from django.db import models
import string
import random
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from distutils.command.config import config
from jsonfield import JSONField
from django.db.models.signals import pre_save
from ezreg.payment import PaymentProcessorManager
from datetime import datetime
from django.db.models.query_utils import Q

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Event(models.Model):
#     STATUS_OPEN = 'open'
#     STATUS_CLOSED = 'closed'
#     STATUSES = ((STATUS_OPEN,'Open'),(STATUS_CLOSED,'Closed'))
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
    group = models.ForeignKey(Group)
    slug = models.SlugField(max_length=100,unique=True,blank=True)
    title = models.CharField(max_length=100,blank=False)
    description = models.TextField(blank=False)
    body = models.TextField(blank=False)
    active = models.BooleanField(default=False)
    capacity = models.IntegerField(blank=True,null=True)
    cancellation_policy = models.TextField(blank=True,null=True)
    open_until = models.DateField()
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
    advertise = models.BooleanField(default=False)
    payment_processors = models.ManyToManyField('PaymentProcessor',through='EventProcessor')
    enable_waitlist = models.BooleanField(default=False)
    waitlist_message = models.TextField(blank=True,null=True)
    @property
    def slug_or_id(self):
        return self.slug if self.slug else self.id
    @property
    def registered(self):
        return self.registrations.filter(status=Registration.STATUS_REGISTERED).count()
    @property
    def waitlisted(self):
        return self.registrations.filter(status=Registration.STATUS_WAITLISTED).count()
    @property
    def cancelled(self):
        return self.registrations.filter(status=Registration.STATUS_CANCELLED).count()
    @property
    def pending(self):
        return self.registrations.filter(Q( status=Registration.STATUS_PENDING_INCOMPLETE)|Q( status=Registration.STATUS_WAITLIST_PENDING)|Q( status=Registration.STATUS_WAITLIST_INCOMPLETE)).count()
    @property
    def registration_open(self):
        return self.active and str(self.open_until)[:10] >= str(datetime.today())[:10] and self.registrations.exclude(status=Registration.STATUS_CANCELLED).count() < self.capacity
    @property
    def waitlist_open(self):
        return self.active and self.enable_waitlist and str(self.open_until)[:10] >= str(datetime.today())[:10] and self.registrations.exclude(status=Registration.STATUS_CANCELLED).count() >= self.capacity
    def __unicode__(self):
        return self.title
    class Meta:
        permissions = (
            ('admin_event', 'Can modify event'),
            ('view_event', 'Can view event details and registrations'),
        )
        
class EventPage(models.Model):
    event = models.ForeignKey('Event',related_name='pages')
    slug = models.SlugField(max_length=50,unique=True,blank=True)
    heading = models.CharField(max_length=40)
    body = models.TextField()
    class Meta:
        unique_together = (('event','slug'))

class Price(models.Model):
    event = models.ForeignKey('Event',related_name='prices')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    def __unicode__(self):
        return mark_safe('<span title="%s"><b>$%s</b> - %s</span>' % (self.description,str(self.amount),self.name))
    
class Registration(models.Model):
    STATUS_REGISTERED = 'REGISTERED'
    STATUS_PENDING_INCOMPLETE = 'PENDING_INCOMPLETE'
    STATUS_WAITLISTED = 'WAITLISTED'
    STATUS_WAITLIST_INCOMPLETE = 'WAITLIST_INCOMPLETE'
    STATUS_WAITLIST_PENDING = 'WAITLIST_PENDING'
    STATUS_CANCELLED = 'CANCELLED'
    STATUSES = ((STATUS_REGISTERED,'Registered'),(STATUS_PENDING_INCOMPLETE,'Pending'),(STATUS_WAITLIST_PENDING,'Pending from waitlist'),(STATUS_WAITLISTED,'Waitlisted'),(STATUS_WAITLIST_INCOMPLETE,'Waitlist- incomplete'),(STATUS_CANCELLED,'Cancelled'))
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
    status = models.CharField(max_length=25,choices=STATUSES,null=True,blank=True)
    event = models.ForeignKey('Event',related_name='registrations')
    registered = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    institution = models.CharField(max_length=100,null=True,blank=True)
    group_name = models.CharField(max_length=100,null=True,blank=True)
    special_requests = models.TextField(null=True,blank=True)
    price = models.ForeignKey('Price',null=True,blank=True)
    @property
    def waitlist_place(self):
        if self.status != Registration.STATUS_WAITLISTED:
            return None
        return self.event.registrations.filter(status=Registration.STATUS_WAITLISTED,registered__lte=self.registered).count() + 1
    @property
    def is_waitlisted(self):
        print self.id
        return self.status in [Registration.STATUS_WAITLIST_INCOMPLETE, Registration.STATUS_WAITLISTED]
    @property
    def is_waitlist_pending(self):
        return self.status == Registration.STATUS_WAITLIST_PENDING
    class Meta:
        unique_together = (('email','event'))
   
class Payment(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_CHOICES = ((STATUS_UNPAID,'Unpaid'),(STATUS_PENDING,'Pending'),(STATUS_PAID,'Paid'))
    processor = models.ForeignKey('PaymentProcessor',null=True,blank=True)
    status = models.CharField(max_length=10,default=STATUS_UNPAID,choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(blank=True,null=True)
    registration = models.OneToOneField(Registration,related_name='payment')
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    data = JSONField(null=True,blank=True)
    def get_post_form(self):
        processor = self.processor.get_processor()
        return processor.get_post_form(self)
    
class PaymentProcessor(models.Model):
    processor_id = models.CharField(max_length=30)
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    config = JSONField()
    def get_processor(self):
        manager = PaymentProcessorManager()
        return manager.get_processor(self.processor_id)
    def get_configuration_form(self):
        processor = self.get_processor()
        return processor.get_configuration_form()
    def __unicode__(self):
        return self.name

class EventProcessor(models.Model):
    event = models.ForeignKey('Event')
    processor = models.ForeignKey('PaymentProcessor')
    
def save_event_processor(sender,instance,**kwargs):
    print '!!!!!!!!!!!!!!!!!!!'
    if instance.processor.group != instance.event.group:
        raise Exception("Attempted to use a payment processor for a group that was different than the event group.")
pre_save.connect(save_event_processor, sender=EventProcessor)

