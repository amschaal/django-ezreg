from django.db import models
import string
import random
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from distutils.command.config import config
from jsonfield import JSONField
from django.db.models.signals import pre_save
from ezreg.payment import PaymentProcessorManager

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
    open_until = models.DateField(blank=True,null=True)
    advertise = models.BooleanField(default=False)
    payment_processors = models.ManyToManyField('PaymentProcessor',through='EventProcessor')
    def __unicode__(self):
        return self.title
    class Meta:
        permissions = (
            ('admin_event', 'Can modify event'),
            ('view_event', 'Can view event details and registrations'),
        )

class EventPage(models.Model):
    event = models.ForeignKey(Event,related_name='pages')
    slug = models.SlugField(max_length=50,unique=True,blank=True)
    heading = models.CharField(max_length=40)
    body = models.TextField()
    class Meta:
        unique_together = (('event','slug'))

class Price(models.Model):
    event = models.ForeignKey(Event,related_name='prices')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    hidden = models.BooleanField(default=False)
    def __unicode__(self):
        return mark_safe('<span title="%s"><b>$%s</b> - %s</span>' % (self.description,str(self.amount),self.name))
    
class Registration(models.Model):
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
    event = models.ForeignKey(Event,related_name='registrations')
    registered = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=50,blank=False)
    last_name = models.CharField(max_length=50,blank=False)
    email = models.EmailField(blank=False)
    institution = models.CharField(max_length=100)
    group_name = models.CharField(max_length=100)
    special_requests = models.TextField()
    price = models.ForeignKey(Price,null=True,blank=True)
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
    event = models.ForeignKey(Event)
    processor = models.ForeignKey(PaymentProcessor)
    
def save_event_processor(sender,instance,**kwargs):
    print '!!!!!!!!!!!!!!!!!!!'
    if instance.processor.group != instance.event.group:
        raise Exception("Attempted to use a payment processor for a group that was different than the event group.")
pre_save.connect(save_event_processor, sender=EventProcessor)

