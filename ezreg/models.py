from django.db import models
import string
import random
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from distutils.command.config import config
from jsonfield import JSONField
from django.db.models.signals import pre_save
from ezreg.payment import PaymentProcessorManager
from datetime import datetime, timedelta
from django.db.models.query_utils import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from mailqueue.models import MailerMessage
from ezreg.fields import EmailListField
from django.core.validators import MinLengthValidator
from django_bleach.models import BleachField
from django.utils import timezone

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Organizer(models.Model):
    slug = models.SlugField(max_length=50,unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    def __unicode__(self):
        return self.name

class OrganizerUserPermission(models.Model):
    PERMISSION_ADMIN = 'admin'
    PERMISSION_MANAGE_PROCESSORS = 'manage_processors'
    PERMISSION_VIEW = 'view'
    PERMISSION_CHOICES=((PERMISSION_ADMIN,'Administer'),(PERMISSION_VIEW,'View registrations'),(PERMISSION_MANAGE_PROCESSORS,'Manage payment processors'))
    organizer = models.ForeignKey(Organizer,related_name="user_permissions")
    user = models.ForeignKey(User)
    permission = models.CharField(max_length=25,choices=PERMISSION_CHOICES)
    class Meta:
        unique_together = (('organizer','user','permission'))
    def __unicode__(self):
        return '%s - %s: %s'%(self.organizer,self.permission,self.user)

class Event(models.Model):
#     STATUS_OPEN = 'open'
#     STATUS_CLOSED = 'closed'
#     STATUSES = ((STATUS_OPEN,'Open'),(STATUS_CLOSED,'Closed'))
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
#     group = models.ForeignKey(Group)
    organizer = models.ForeignKey(Organizer,related_name='events')
    slug = models.SlugField(max_length=100,unique=True,blank=True)
    title = models.CharField(max_length=150,blank=False)
    description = models.TextField(blank=False)
    body = BleachField(blank=False)
    active = models.BooleanField(default=False)
    capacity = models.PositiveSmallIntegerField(blank=True,null=True)
    cancellation_policy = BleachField(blank=True,null=True)
    open_until = models.DateField()
    start_time = models.DateTimeField(blank=True,null=True)
    end_time = models.DateTimeField(blank=True,null=True)
    contact = models.TextField()
    display_address = models.BooleanField(default=True)
    address = models.TextField(blank=True,null=True)
    advertise = models.BooleanField(default=False)
    payment_processors = models.ManyToManyField('PaymentProcessor',through='EventProcessor')
    enable_waitlist = models.BooleanField(default=False)
    enable_application = models.BooleanField(default=False)
    waitlist_message = models.TextField(blank=True,null=True)
    bcc = EmailListField(max_length=250,blank=True,null=True)
    from_addr = models.EmailField(max_length=50,blank=True,null=True)
    expiration_time = models.PositiveSmallIntegerField(default=30)
    ical = models.FilePathField(path=settings.FILES_ROOT,match='*.ics',blank=True,null=True)
    logo = models.ImageField(upload_to='logos/',null=True,blank=True)
    form_fields = JSONField(null=True, blank=True)
    outside_url = models.URLField(null=True,blank=True)
    @property
    def slug_or_id(self):
        return self.slug if self.slug else self.id
    @property
    def registered(self):
        return self.registrations.filter(status=Registration.STATUS_REGISTERED).exclude(test=True).count()
    @property
    def waitlisted(self):
        return self.registrations.filter(status=Registration.STATUS_WAITLISTED).exclude(test=True).count()
    @property
    def applied(self):
        return self.registrations.filter(status=Registration.STATUS_APPLIED).exclude(test=True).count()
    @property
    def cancelled(self):
        return self.registrations.filter(status=Registration.STATUS_CANCELLED).exclude(test=True).count()
    @property
    def pending(self):
        return self.registrations.filter(Q( status=Registration.STATUS_PENDING_INCOMPLETE)|Q( status=Registration.STATUS_WAITLIST_PENDING)|Q( status=Registration.STATUS_WAITLIST_INCOMPLETE)|Q( status=Registration.STATUS_APPLY_INCOMPLETE)).exclude(test=True).count()
    
    @property
    def registration_enabled(self):
#         if self.enable_application:
        return self.active and str(self.open_until)[:10] >= str(datetime.today())[:10]
#         return self.active and str(self.open_until)[:10] >= str(datetime.today())[:10] and self.registrations.exclude(status=Registration.STATUS_CANCELLED).count() < self.capacity
    @property
    def is_full(self):
        return self.registrations.exclude(status=Registration.STATUS_CANCELLED).exclude(test=True).count() >= self.capacity
    def can_register(self):
        return self.registration_enabled and not self.is_full and not self.enable_application
    def can_waitlist(self):
        return self.registration_enabled and self.enable_waitlist and self.is_full
    def can_apply(self):
        return self.registration_enabled and self.enable_application
    def registration_open(self):
        return self.registration_enabled and (self.can_register() or self.can_apply() or self.can_waitlist())
    def delete_expired_registrations(self):
        self.registrations.filter(registered__lte=(timezone.now()-timedelta(minutes=self.expiration_time)),status__in=[Registration.STATUS_APPLY_INCOMPLETE,Registration.STATUS_PENDING_INCOMPLETE,Registration.STATUS_WAITLIST_INCOMPLETE]).delete()
    def generate_event_ical(self):
        from icalendar import Calendar, Event, vText, vCalAddress
        calendar = Calendar()
        cevent = Event()
        if self.start_time:
            cevent.add('dtstart', self.start_time)
            if self.end_time:
                cevent.add('dtend', self.end_time)
        if self.address:
            cevent.add('location',vText(self.address))
#         organizer = vCalAddress('')
#         organizer.params['cn']= vText(self.organizer.name)
#         cevent['organizer']=organizer
        cevent.add('summary', self.title)
        calendar.add_component(cevent)
        return calendar.to_ical()
    def get_user_permissions(self, user):
        if user.is_superuser:
            return [p[0] for p in OrganizerUserPermission.PERMISSION_CHOICES]
        return [p.permission for p in OrganizerUserPermission.objects.filter(user=user,organizer=self.organizer)]
    def __unicode__(self):
        return self.title
    class Meta:
        permissions = (
            ('admin_event', 'Can modify event'),
            ('view_event', 'Can view event details and registrations'),
        )
def event_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'logos/{0}/{1}'.format(instance.organizer.id, filename)
   
class EventPage(models.Model):
    event = models.ForeignKey('Event',related_name='pages')
    slug = models.SlugField(max_length=50,blank=True)
    heading = models.CharField(max_length=40)
    body = BleachField()
    class Meta:
        unique_together = (('event','slug'))

class Price(models.Model):
    event = models.ForeignKey('Event',related_name='prices')
    order = models.PositiveSmallIntegerField(null=True,blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    coupon_code = models.CharField(max_length=25,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    def __unicode__(self):
        return mark_safe('<span title="%s"><b>$%s</b> - %s</span>' % (self.description,str(self.amount),self.name))
    class Meta:
        unique_together = (('event','coupon_code'))
    
class Registration(models.Model):
    STATUS_REGISTERED = 'REGISTERED'
    STATUS_PENDING_INCOMPLETE = 'PENDING_INCOMPLETE'
    STATUS_WAITLISTED = 'WAITLISTED'
    STATUS_WAITLIST_INCOMPLETE = 'WAITLIST_INCOMPLETE'
    STATUS_WAITLIST_PENDING = 'WAITLIST_PENDING'
    STATUS_APPLIED = 'APPLIED'
    STATUS_APPLY_INCOMPLETE = 'APPLY_INCOMPLETE'
    STATUS_APPLIED_ACCEPTED = 'APPLIED_ACCEPTED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUSES = ((STATUS_REGISTERED,'Registered'),
                (STATUS_PENDING_INCOMPLETE,'Pending'),
                (STATUS_WAITLIST_PENDING,'Pending from waitlist'),
                (STATUS_WAITLISTED,'Waitlisted'),
                (STATUS_WAITLIST_INCOMPLETE,'Waitlist- incomplete'),
                (STATUS_APPLIED_ACCEPTED,'Application accepted'),
                (STATUS_APPLIED,'Applied'),
                (STATUS_APPLY_INCOMPLETE,'Application- incomplete'),
                (STATUS_CANCELLED,'Cancelled')
                
                )
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
    key = models.CharField(max_length=10,default=id_generator)
    status = models.CharField(max_length=25,choices=STATUSES,null=True,blank=True)
    event = models.ForeignKey('Event',related_name='registrations')
    registered = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
#     institution = models.CharField(max_length=100,null=True,blank=True)
#     department = models.CharField(max_length=100,null=True,blank=True)
#     special_requests = models.TextField(null=True,blank=True)
    price = models.ForeignKey('Price',null=True,blank=True)
    email_messages = models.ManyToManyField(MailerMessage,related_name='registrations')
    test = models.BooleanField(default=False)
    registered_by = models.ForeignKey(User,null=True,blank=True)
    admin_notes = models.TextField(null=True,blank=True)
    data = JSONField(null=True, blank=True)
    def get_form_value(self,name):
        if not self.data:
            return None
        return self.data[name] if self.data.has_key(name) else None
    def get_registration_fields(self):
        fields = [
                  {'name':'first_name','label':'First name','value':self.first_name},
                  {'name':'last_name','label':'Last name','value':self.last_name},
                  {'name':'email','label':'Email','value':self.email}
                 ]
        if self.data:
            for field in self.event.form_fields:
                if field.has_key('name'):
                    if self.data.has_key(field['name']):
                        fields.append({'name':field['name'],'label':field['label'],'value':self.data[field['name']]})
        return fields
    @property
    def waitlist_place(self):
        if self.status != Registration.STATUS_WAITLISTED:
            return None
        return self.event.registrations.filter(status=Registration.STATUS_WAITLISTED,registered__lte=self.registered).count() + 1
    @property
    def is_waitlisted(self):
        return self.status in [Registration.STATUS_WAITLIST_INCOMPLETE, Registration.STATUS_WAITLISTED]
    @property
    def is_application(self):
        return self.status in [Registration.STATUS_APPLY_INCOMPLETE, Registration.STATUS_APPLIED]
    @property
    def is_waitlist_pending(self):
        return self.status == Registration.STATUS_WAITLIST_PENDING
    @property
    def is_accepted(self):
        return self.status == Registration.STATUS_APPLIED_ACCEPTED
    def get_payment(self):
        try:
            return self.payment
        except Payment.DoesNotExist:
            return None
#     class Meta:
#         unique_together = (('email','event'))
   
class Payment(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PENDING = 'PENDING'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_INVALID_AMOUNT = 'INVALID_AMOUNT'
    STATUS_PAID = 'PAID'
    STATUS_ERROR = 'ERROR'
    STATUS_CHOICES = ((STATUS_UNPAID,'Unpaid'),(STATUS_PENDING,'Pending'),(STATUS_PAID,'Paid'),(STATUS_CANCELLED,'Cancelled'),(STATUS_INVALID_AMOUNT,'Invalid Amount'),(STATUS_ERROR,'Error'))
    processor = models.ForeignKey('PaymentProcessor',null=True,blank=True)
    status = models.CharField(max_length=20,default=STATUS_UNPAID,choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(blank=True,null=True)
    registration = models.OneToOneField(Registration,related_name='payment')
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    refunded = models.DecimalField(decimal_places=2,max_digits=7,null=True,blank=True)
    external_id = models.CharField(max_length=50,null=True,blank=True)
    data = JSONField(null=True,blank=True)
    def get_post_form(self):
        processor = self.processor.get_processor()
        return processor.get_post_form(self)
    def get_form(self):
        processor = self.processor.get_processor()
        return processor.get_form()
    def get_populated_form(self):
        form_class = self.get_form()
        if not form_class:
            return None
        if self.data:
            return form_class(self.data,event=self.registration.event)
        else:
            return form_class(event=self.registration.event)

class PaymentProcessor(models.Model):
    processor_id = models.CharField(max_length=30)
#     group = models.ForeignKey(Group)
    organizer = models.ForeignKey(Organizer,related_name='payment_processors')
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
    if instance.processor.organizer != instance.event.organizer:
        raise Exception("Attempted to use a payment processor for an organizer that was different than the event organizer.")
pre_save.connect(save_event_processor, sender=EventProcessor)

def save_event_ical(sender,instance,**kwargs):
    path = os.path.join(settings.FILES_ROOT, instance.id, 'event.ics')
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    ics = open(path,'wb')
    ics.write(instance.generate_event_ical())
    ics.close()
    instance.ical = path
pre_save.connect(save_event_ical, sender=Event)
