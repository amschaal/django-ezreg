from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from datetime import datetime

from ezreg.models import Event, Price, Registration, PaymentProcessor, Organizer,\
    OrganizerUserPermission, Payment
from ezreg.payment import PaymentProcessorManager
from django.forms.widgets import  TextInput
from django.db.models.query_utils import Q
from datetimewidget.widgets import DateTimeWidget, DateWidget

def _raw_value(form, fieldname):
    field = form.fields[fieldname]
    prefix = form.add_prefix(fieldname)
    return field.widget.value_from_datadict(form.data, form.files, prefix)

class AngularDatePickerInput(TextInput):
    def render(self, name, value, attrs={}):
        attrs.update({
                      'datepicker-popup':"yyyy-MM-dd", 
                      'is-open':"datepicker."+name, 
                    'ng-click':"datepicker.%s=true"%name, 
                      'ng-model':name,
                      }
                     )
        if value:
            attrs['ng-init']="%s='%s'"%(name,str(value))
        html =  super(AngularDatePickerInput,self).render(name, value, attrs)
        html += """
              <span class="input-group-btn">
                <button type="button" class="btn btn-default" ng-click="datepicker.%(name)s=true"><i class="glyphicon glyphicon-calendar"></i></button>
              </span></p>
              """%{'name':name}
        return '<p class="input-group">'+html


class EventForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(EventForm,self).__init__(*args, **kwargs)
        self.fields['organizer'].queryset = Organizer.objects.filter(user_permissions__user=user,user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN)
        self.fields['open_until'].required = False
        #Make open_until default to start_time if not provided
        data = self.data.copy()
        data['open_until'] = self.data.get('open_until') or self.data.get('start_time','')[:10]
        self.data = data
    body = forms.CharField(label='Event page',help_text='This is the main page for your event and should contain most information about your event.',widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    description = forms.CharField(label='Brief event description',help_text='This should be a brief description of your event, and will be displayed during the registration process.',widget=TinyMCE(attrs={'cols': 80, 'rows': 15}))
    cancellation_policy = forms.CharField(required=False,widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and (start_time > end_time):
            self.add_error('start_time', 'Start time should not be later than end time.')
    class Meta:
        model=Event
        fields = ('organizer','title','active','advertise','enable_waitlist','enable_application','capacity',
                  'slug','logo','title','description','body','cancellation_policy','open_until',
                  'start_time','end_time','contact','display_address','address','waitlist_message','bcc','from_addr','expiration_time','outside_url')
#         exclude = ('id','payment_processors','ical','form_fields','group')
        labels = {
                  'start_time': 'Event Start Time',
                  'end_time': 'Event End Time',
                  'active':'Activate registration',
                  'from_addr':'From address',
                  'address':'Location',
                  'display_address': 'Display location',
                  'expiration_time': 'Expiration time (minutes)',
                  'slug':'Friendly URL',
        }
        help_texts = {
            'slug': 'This will be used in the event URL.  Use only alphanumeric characters and underscores.',
            'description': 'This description will appear during the registration process.',
            'advertise':'Select this if you want the event to show up on the home page.',
            'enable_waitlist':'Once the event fills up, allow users to waitlist.',
            'enable_application':'Users will be able to fill out all fields not related to payment, marking their status as applied.  The event coordinator will need to select which applications can proceed to complete registration.  DO NOT USE with waitlist.',
            'bcc':'Comma delimited email addresses that should be BCCed with each registration email.',
            'from_addr':'Email address that registration emails should be sent from, if different from the default.',
            'display_address':'Should the location be shown on the event page?',
            'contact':'Who is the contact for the event?  Include details like name, email or phone number.',
            'address':'Where is the event located?  This will be included in the ical event sent with confirmation emails.',
            'expiration_time':'Registrations must be completed within this time limit.',
            'open_until':'Defaults to start time if not provided.',
            'logo': 'Optionally upload a logo to replace the default website logo.  Image will be scaled to a maximum height of 100px.',
            'outside_url': 'Optionally provide a URL to an outside event.  If this is set, registration through the system will not be possible.',
        }
        widgets = {
                      'open_until':DateWidget(attrs={'id':"open_until"}, usel10n = True, bootstrap_version=3),
                        #Use localization and bootstrap 3
                        'start_time': DateTimeWidget(attrs={'id':"start_time"},options={'format': 'yyyy-mm-dd hh:ii','minuteStep':15}, usel10n = False, bootstrap_version=3),
                        'end_time': DateTimeWidget(attrs={'id':"end_time"}, options={'format': 'yyyy-mm-dd hh:ii','minuteStep':15}, usel10n = False, bootstrap_version=3)
                   }
        
class PaymentProcessorForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PaymentProcessorForm,self).__init__(*args, **kwargs)
        self.fields['organizer'].queryset = Organizer.objects.filter(user_permissions__user=user,user_permissions__permission=OrganizerUserPermission.PERMISSION_MANAGE_PROCESSORS)
        self.PaymentProcessors = PaymentProcessorManager()
        processor_choices = self.PaymentProcessors.get_choices()
        self.fields['processor_id'].widget = forms.widgets.Select(choices=processor_choices)
    class Meta:
        model= PaymentProcessor
        fields = ('processor_id','organizer','name','description','hidden')

class RegistrationForm(forms.ModelForm):
    template = 'ezreg/registration/form.html'
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event',None)
        self.admin = kwargs.pop('admin',False)
        super(RegistrationForm,self).__init__(*args, **kwargs)
        if not self.admin:
            self.fields.pop('admin_notes')
        for field in ['first_name','last_name','email']:
            self.fields[field].required=True
    def clean_email(self):
        email = self.cleaned_data['email']
        print self.instance.id
        if email and not self.instance.test:
            if Registration.objects.filter(email=email, event=self.event).exclude(id=self.instance.id).exclude(status__in=[Registration.STATUS_CANCELLED]).exclude(test=True).count() != 0:
                raise ValidationError('A registration with that email already exists.')
        return email
    class Meta:
        model=Registration
#         exclude = ('id','event','price','status')
        fields = ('first_name','last_name','email','admin_notes')#,'institution','department','special_requests'
        
class AdminRegistrationForm(forms.ModelForm):
    class Meta:
        model=Registration
        fields = ('first_name','last_name','email','admin_notes')

class AdminRegistrationStatusForm(forms.ModelForm):
    email = forms.CheckboxInput()
    class Meta:
        model=Registration
        fields = ('status',)
        
class PriceForm(forms.Form):
    template = 'ezreg/registration/price.html'
    price = forms.ModelChoiceField(queryset=Price.objects.all(),required=True,empty_label=None,widget=forms.widgets.RadioSelect)
    coupon_code = forms.CharField(required=False)
    payment_method = forms.ModelChoiceField(queryset=PaymentProcessor.objects.all(),required=True,empty_label=None,widget=forms.widgets.RadioSelect)
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super(PriceForm,self).__init__(*args, **kwargs)
        self.setup_coupons()
        self.fields['price'].queryset = self.get_price_queryset()
        self.fields['payment_method'].queryset = self.get_payment_method_queryset() 
    def setup_coupons(self):
        self.data = self.data.copy() #POST querydict is immutable, need to be able to overwrite price for coupon code
        self.coupon_price = None
        if not self.event.prices.filter(coupon_code__isnull=False).count():
            del self.fields['coupon_code']
        else:
            coupon_code = _raw_value(self,'coupon_code')#self._raw_value('coupon_code') #This went away in 1.9
            if coupon_code:
                self.coupon_price = self.available_prices_queryset(include_coupons=True).filter(coupon_code=coupon_code).first()
                if self.coupon_price:
                    self.data[self.add_prefix('price')]=self.coupon_price.id
    def get_payment_method_queryset(self):
        return self.event.payment_processors.filter(hidden=False)
    def available_prices_queryset(self,include_coupons=False):
        qs = self.event.prices.exclude(disable=True).exclude(start_date__isnull=False,start_date__gt=datetime.today()).exclude(end_date__isnull=False,end_date__lt=datetime.today()).order_by('order')
        
        #Exclude any prices that are sold out
        soldout_ids = []
        for price in qs:
            if price.quantity and price.quantity > 0:
                if price.registrations.filter(status__in=[Registration.STATUS_REGISTERED,Registration.STATUS_PENDING_INCOMPLETE]).count() >= price.quantity:
                    soldout_ids.append(price.id)
        if len(soldout_ids)>0:
            qs = qs.exclude(id__in=soldout_ids)

        if include_coupons:
            return qs
        else:
            return qs.filter(Q(coupon_code__isnull=True)|Q(coupon_code=''))
    def get_price_queryset(self):
        prices = self.available_prices_queryset(include_coupons=False)#self.event.prices.exclude(start_date__isnull=False,start_date__gt=datetime.today()).exclude(end_date__isnull=False,end_date__lt=datetime.today()).exclude(coupon_code__isnull=False).order_by('order')
        #Add coupon price if available
        if self.coupon_price:
            price_ids = [p.id for p in prices]+[self.coupon_price.id]
            prices = self.event.prices.filter(id__in=price_ids).order_by('order')#prices #@todo: figure out filter to only allow coupon in addition
        return prices
    def clean_price(self):
        if self.coupon_price:
            self.cleaned_data['price'] = self.coupon_price
        return self.cleaned_data['price']
    def clean_coupon_code(self):
        coupon_code = self.cleaned_data['coupon_code']
        if coupon_code and not self.coupon_price:
                raise ValidationError('Invalid coupon code')
        return coupon_code

#Form that allows admin to choose ANY price for an event 
class AdminPriceForm(forms.Form):
    price = forms.ModelChoiceField(Price.objects.all(),required=True,empty_label=None,widget=forms.widgets.RadioSelect)
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super(AdminPriceForm,self).__init__(*args, **kwargs)
        self.fields['price'].queryset = self.get_price_queryset()
    def get_price_queryset(self):
        prices = self.event.prices.order_by('order')
        return prices


class AdminPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminPaymentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        print "ADMIN PAYMENT FORM"
        if instance and instance.status == Payment.STATUS_PAID:
            print "PAID"
            self.fields['status'].disabled = True
            self.fields['status'].help_text = 'A status of PAID may not be changed.  Refunds may be issued, but the original status must remain.'
    class Meta:
        model=Payment
        fields = ('status','refunded','admin_notes')
    def clean_refunded(self):
        refunded = self.cleaned_data['refunded']
        if refunded and not self.instance.amount or refunded > self.instance.amount:
            raise ValidationError('You cannot refund more than was paid.')
        return refunded


class PriceFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PriceFormsetHelper, self).__init__(*args, **kwargs)
#         self.form_method = 'post'
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout = Layout(
            'name',
            'description',
            'amount',
            'hidden',
        )
        self.render_required_fields = True

#Dummy form for skipping/replacing in registration wizard (because we can't dynamically set forms based on previous form input)
class ConfirmationForm(forms.Form):
    template = 'ezreg/registration/confirm.html'
    accept_policy = forms.BooleanField(label="Accept",required=False)
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(ConfirmationForm,self).__init__(*args, **kwargs)
        if not event.cancellation_policy:
            del self.fields['accept_policy']
    def clean_accept_policy(self):
        accept_policy = self.cleaned_data['accept_policy']
        if not accept_policy:
            raise ValidationError('You must accept the cancellation policy to continue.')
        return accept_policy
    