from django.db import models
import string
import random
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from distutils.command.config import config
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
from django.contrib.postgres.fields import JSONField
import uuid


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Organizer(models.Model):
    slug = models.SlugField(max_length=50,unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    config = JSONField(default=dict)
    def __str__(self):
        return self.name

class OrganizerUserPermission(models.Model):
    PERMISSION_ADMIN = 'admin'
    PERMISSION_MANAGE_PROCESSORS = 'manage_processors'
    PERMISSION_VIEW = 'view'
    PERMISSION_CHOICES=((PERMISSION_ADMIN,'Administer'),(PERMISSION_VIEW,'View registrations'),(PERMISSION_MANAGE_PROCESSORS,'Manage payment processors'))
    organizer = models.ForeignKey(Organizer,related_name="user_permissions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=25,choices=PERMISSION_CHOICES)
    class Meta:
        unique_together = (('organizer','user','permission'))
    def __str__(self):
        return '%s - %s: %s'%(self.organizer,self.permission,self.user)

class Event(models.Model):
#     STATUS_OPEN = 'open'
#     STATUS_CLOSED = 'closed'
#     STATUSES = ((STATUS_OPEN,'Open'),(STATUS_CLOSED,'Closed'))
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
#     group = models.ForeignKey(Group)
    organizer = models.ForeignKey(Organizer,on_delete=models.PROTECT,related_name='events')
    slug = models.SlugField(max_length=100,unique=True,blank=True)
    title = models.CharField(max_length=150,blank=False)
    description = BleachField(blank=False)
    body = BleachField(blank=False)
    active = models.BooleanField(default=False)
    capacity = models.PositiveSmallIntegerField(blank=True,null=True)
    cancellation_policy = BleachField(blank=True,null=True)
    open_until = models.DateField()
    tentative = models.BooleanField(default=False)
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
    hide_header = models.BooleanField(default=False)
    form_fields = JSONField(null=True, blank=True)
    department_field = models.BooleanField(default=True)
    outside_url = models.URLField(null=True,blank=True)
    external_payment_url = models.URLField(null=True,blank=True)
    bill_to_account = models.CharField(null=True, blank=True, max_length=30)
    billed = models.BooleanField(default=False)
    billing_notes = models.TextField(null=True, blank=True)
    billed_on = models.DateTimeField(null=True, blank=True)
    billed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    config = JSONField(default=dict)
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
    def accepted(self):
        return self.registrations.filter(status=Registration.STATUS_APPLIED_ACCEPTED).exclude(test=True).count()
    @property
    def registration_closed(self):
        return self.open_until and str(self.open_until)[:10] < str(datetime.today())[:10]
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
        if user.is_staff:
            return [p[0] for p in OrganizerUserPermission.PERMISSION_CHOICES]
        return [p.permission for p in OrganizerUserPermission.objects.filter(user=user,organizer=self.organizer)]
    def total_revenue(self, statuses=[], subtract_refunds=True, payment_processor_ids=[], payment_statuses=[]):
        from django.db.models.aggregates import Sum
        statuses = statuses if len(statuses) > 0 else [Registration.STATUS_REGISTERED]
        payment_statuses = payment_statuses if len(payment_statuses) > 0 else [Payment.STATUS_PAID, Payment.STATUS_PENDING]
        #include all registrations of a certain status AND paid registrations, regardless of registration status
        qs = Payment.objects.filter(registration__event=self, status__in=payment_statuses).filter(Q(registration__status__in=statuses)|Q(status=Payment.STATUS_PAID)).exclude(registration__test=True)
        if len(payment_processor_ids) > 0:
            qs = qs.filter(processor__processor_id__in=payment_processor_ids)
        
        totals = qs.aggregate(total=Sum('amount'),refunded=Sum('refunded'))
        if not totals['total']:
            return 0
        elif subtract_refunds and totals['refunded']:
            return totals['total'] - totals['refunded']
        else:
            return totals['total']
    @property
    def revenue(self):
        return round(self.total_revenue(), 2)
    @property
    def credit_card_revenue(self):
        return round(self.total_revenue(payment_processor_ids=['touchnet_payment_processor'],payment_statuses=[Payment.STATUS_PAID]), 2)
    @property
    def service_charges(self):
        return round(float(self.revenue) * (settings.SERVICE_CHARGE_PERCENT/100.0), 2)
    @property
    def credit_card_charges(self):
        return round(float(self.credit_card_revenue) * (settings.CREDIT_CARD_CHARGE_PERCENT/100.0), 2)
    @property
    def service_charges_text(self):
        return '${0:.2f} @ {1}% = ${2:.2f}'.format(self.revenue,settings.SERVICE_CHARGE_PERCENT, self.service_charges)
    @property
    def credit_card_charges_text(self):
        return '${0:.2f} @ {1}% = ${2:.2f}'.format(self.credit_card_revenue,settings.CREDIT_CARD_CHARGE_PERCENT, self.credit_card_charges)
    @property
    def total_charges(self):
        return round(self.service_charges + self.credit_card_charges, 2)
    def __str__(self):
        return self.title
    class Meta:
        permissions = (
            ('admin_event', 'Can modify event'),
#             ('view_event', 'Can view event details and registrations'),
            ('bill_event', 'Can bill events')
        )
def event_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'logos/{0}/{1}'.format(instance.organizer.id, filename)
   
class EventPage(models.Model):
    event = models.ForeignKey('Event',related_name='pages', on_delete=models.CASCADE)
    index = models.IntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=50,blank=True,null=True)
    heading = models.CharField(max_length=40)
    body = BleachField()
    class Meta:
        unique_together = (('event','slug'))
        ordering = ('index', 'id')

# class EventText(models.Model):
#     TYPE_POST_PRICE = 'POST_PRICE'
#     TYPE_EMAIL_CONFIRMATION = 'EMAIL_CONFIRMATION'
#     TYPES = ((TYPE_POST_PRICE,TYPE_POST_PRICE),(TYPE_EMAIL_CONFIRMATION,TYPE_EMAIL_CONFIRMATION))
#     type = models.CharField(max_length=25,choices=EventText.TYPES)
#     event = models.ForeignKey('Event',related_name='texts')
#     html = BleachField(null=True,blank=True)
#     text = models.TextField(null=True,blank=True)
#     class Meta:
#         unique_together = (('event','type'))

class Price(models.Model):
    event = models.ForeignKey('Event',related_name='prices', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(null=True,blank=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    coupon_code = models.CharField(max_length=25,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    quantity = models.PositiveIntegerField(null=True)
    disable = models.BooleanField(default=False)
    def __str__(self):
        return mark_safe('<span title="%s"><b>$%s</b> - %s</span>' % (self.description,str(self.amount),self.name))
    class Meta:
        ordering = ('order',)
#         unique_together = (('event','coupon_code'))
    
class Registration(models.Model):
    STATUS_REGISTERED = 'REGISTERED'
    STATUS_PENDING_INCOMPLETE = 'PENDING_INCOMPLETE'
    STATUS_WAITLISTED = 'WAITLISTED'
    STATUS_WAITLIST_INCOMPLETE = 'WAITLIST_INCOMPLETE'
    STATUS_WAITLIST_PENDING = 'WAITLIST_PENDING'
    STATUS_APPLIED = 'APPLIED'
    STATUS_APPLY_INCOMPLETE = 'APPLY_INCOMPLETE'
    STATUS_APPLIED_ACCEPTED = 'APPLIED_ACCEPTED'
    STATUS_APPLIED_DENIED = 'APPLIED_DENIED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUSES = ((STATUS_REGISTERED,'Registered'),
                (STATUS_PENDING_INCOMPLETE,'Pending'),
                (STATUS_WAITLIST_PENDING,'Pending from waitlist'),
                (STATUS_WAITLISTED,'Waitlisted'),
                (STATUS_WAITLIST_INCOMPLETE,'Waitlist- incomplete'),
                (STATUS_APPLIED_ACCEPTED,'Application accepted'),
                (STATUS_APPLIED_DENIED,'Application denied'),
                (STATUS_APPLIED,'Applied'),
                (STATUS_APPLY_INCOMPLETE,'Application- incomplete'),
                (STATUS_CANCELLED,'Cancelled')
                )
    id = models.CharField(max_length=10,default=id_generator,primary_key=True)
    key = models.CharField(max_length=10,default=id_generator)
    status = models.CharField(max_length=25,choices=STATUSES,null=True,blank=True)
    event = models.ForeignKey('Event',related_name='registrations', on_delete=models.CASCADE)
    registered = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
#     institution = models.CharField(max_length=100,null=True,blank=True)
    department = models.CharField(max_length=100,null=True,blank=True)
#     special_requests = models.TextField(null=True,blank=True)
    price = models.ForeignKey('Price',null=True,blank=True,on_delete=models.PROTECT,related_name='registrations')
    email_messages = models.ManyToManyField(MailerMessage,related_name='registrations')
    test = models.BooleanField(default=False)
    registered_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    admin_notes = models.TextField(null=True,blank=True)
    data = JSONField(null=True, blank=True)
    def get_form_value(self,name):
        if not self.data:
            return None
        return self.data[name] if name in self.data else None
    def get_registration_fields(self):
        fields = [
                  {'name':'first_name','label':'First name','value':self.first_name},
                  {'name':'last_name','label':'Last name','value':self.last_name},
                  {'name':'email','label':'Email','value':self.email},
                  {'name':'department','label':'Department','value':self.department}
                 ]
        if self.data:
            for field in self.event.form_fields:
                if 'name' in field:
                    if field['name'] in self.data:
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
    @property
    def display(self):
        return '{}, {} ({})'.format(self.last_name, self.first_name, self.email)
    @property
    def paid(self):
        return getattr(getattr(self,'payment',None),'status',None) == Payment.STATUS_PAID
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
    processor = models.ForeignKey('PaymentProcessor',null=True,blank=True,on_delete=models.PROTECT)
    status = models.CharField(max_length=20,default=STATUS_UNPAID,choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(blank=True,null=True)
    registration = models.OneToOneField(Registration,related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    refunded = models.DecimalField(decimal_places=2,max_digits=7,null=True,blank=True)
    external_id = models.CharField(max_length=50,null=True,blank=True)
    data = JSONField(null=True,blank=True)
    admin_notes = models.TextField(null=True, blank=True)
    @property
    def amount_remaining(self):
        return self.amount - self.refunded if self.refunded else self.amount
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
    def get_additional_email_text(self):
        return self.processor.get_processor().get_additional_email_text(self)

class Refund(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = ((STATUS_PENDING,STATUS_PENDING),(STATUS_CANCELLED,STATUS_CANCELLED),(STATUS_COMPLETED,STATUS_COMPLETED))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey(Registration, related_name="refunds", on_delete=models.CASCADE)
    requester = models.ForeignKey(User, related_name="requested_refunds", on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default=STATUS_PENDING, choices=STATUS_CHOICES)
    amount = models.DecimalField(decimal_places=2,max_digits=7)
    admin = models.ForeignKey(User, null=True, blank=True, related_name="approved_refunds", on_delete=models.PROTECT)
    updated = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ('-requested',)
    def set_status(self, status, user):
        if self.status == Refund.STATUS_COMPLETED:
            raise Exception("Refund has already been completed and cannot be undone.")
        if self.status == Refund.STATUS_CANCELLED:
            raise Exception("Refund has been cancelled and cannot be undone.")
        self.status = status
        self.admin = user
        self.updated = timezone.now()
        self.save()
        if status == Refund.STATUS_COMPLETED:
            if self.registration.payment.refunded:
                self.registration.payment.refunded += self.amount            
            else:
                self.registration.payment.refunded = self.amount
            self.registration.payment.save()
    @property
    def can_cancel(self):
        return self.status == Refund.STATUS_PENDING
    @property
    def can_complete(self):
        return self.status == Refund.STATUS_PENDING and self.amount <= self.registration.payment.amount_remaining

class PaymentProcessor(models.Model):
    processor_id = models.CharField(max_length=30)
#     group = models.ForeignKey(Group)
    organizer = models.ForeignKey(Organizer,on_delete=models.PROTECT,related_name='payment_processors')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    config = JSONField(default=dict)
    def get_processor(self):
        manager = PaymentProcessorManager()
        return manager.get_processor(self.processor_id)
    def get_configuration_form(self):
        processor = self.get_processor()
        return processor.get_configuration_form()
    @staticmethod
    def get_user_queryset(user):
        if user.is_staff:
            return PaymentProcessor.objects.all()
        OUPs = OrganizerUserPermission.objects.filter(user=user,permission=OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS)
        return PaymentProcessor.objects.filter(organizer__in=[oup.organizer_id for oup in OUPs])
    def __str__(self):
        return self.name

class EventProcessor(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    processor = models.ForeignKey('PaymentProcessor', on_delete=models.CASCADE)



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

def user_display(self):
    return '{}, {}'.format(self.last_name, self.first_name)
#     return '{}, {} ({})'.format(self.last_name, self.first_name, self.email)
User.display = user_display