from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from datetime import datetime

from ezreg.models import Event, Price, Registration, PaymentProcessor, Organizer,\
    OrganizerUserPermission
from ezreg.payment import PaymentProcessorManager
from django.forms.widgets import  TextInput
from django.db.models.query_utils import Q
from datetimewidget.widgets import DateTimeWidget, DateWidget

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
#         self.fields['group'].queryset = user.groups.all()
        self.fields['organizer'].queryset = Organizer.objects.filter(user_permissions__user=user,user_permissions__permission=OrganizerUserPermission.PERMISSION_ADMIN)
#         self.fields['open_until'].widget.attrs['ng-init']="dt='%s';"% self.instance.open_until
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    cancellation_policy = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model=Event
        exclude = ('id','payment_processors','ical','form_fields','group')
        labels = {
                  'start_time': 'Event Start Time',
                  'end_time': 'Event End Time',
                  'active':'Activate registration',
                  'from_addr':'From address'
        }
        help_texts = {
            'slug': 'The slug will be used in the event URL.  Use only alphanumeric characters and underscores.',
            'description': 'This description will appear during the registration process.',
            'advertise':'Select this if you want the event to show up on the home page.',
            'enable_waitlist':'Once the event fills up, allow users to waitlist.',
            'enable_application':'Users will be able to fill out all fields not related to payment, marking their status as applied.  The event coordinator will need to select which applications can proceed to complete registration.  DO NOT USE with waitlist.',
            'bcc':'Comma delimited email addresses that should be BCCed with each registration email.',
            'from_addr':'Email address that registration emails should be sent from, if different from the default.'
        }
        widgets = {
#                     'open_until':forms.TextInput(attrs={'datepicker-popup':"yyyy-MM-dd", 'is-open':"blah", 'ng-click':"blah=true", 'ng-model':"dt"})
                      'open_until':DateWidget(attrs={'id':"open_until"}, usel10n = True, bootstrap_version=3),
                        #Use localization and bootstrap 3
                        'start_time': DateTimeWidget(attrs={'id':"start_time"}, usel10n = True, bootstrap_version=3),
                        'end_time': DateTimeWidget(attrs={'id':"end_time"}, usel10n = True, bootstrap_version=3)
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
        super(RegistrationForm,self).__init__(*args, **kwargs)
        for field in ['first_name','last_name','email']:
            self.fields[field].required=True
    def clean_email(self):
        email = self.cleaned_data['email']
        print self.instance.id
        if email:
            if Registration.objects.filter(email=email, event=self.event).exclude(id=self.instance.id).exclude(status=Registration.STATUS_CANCELLED).count() != 0:
                raise ValidationError('A registration with that email already exists.')
        return email
    class Meta:
        model=Registration
#         exclude = ('id','event','price','status')
        fields = ('first_name','last_name','email')#,'institution','department','special_requests'
        
class AdminRegistrationForm(forms.ModelForm):
    class Meta:
        model=Registration
        fields = ('first_name','last_name','email')

class AdminRegistrationStatusForm(forms.ModelForm):
    email = forms.CheckboxInput()
    class Meta:
        model=Registration
        fields = ('status',)
        
class PriceForm(forms.Form):
    template = 'ezreg/registration/price.html'
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(PriceForm,self).__init__(*args, **kwargs)
        self.fields['price'].queryset = event.prices.exclude(start_date__isnull=False,start_date__gt=datetime.today()).exclude(end_date__isnull=False,end_date__lt=datetime.today())
        self.fields['payment_method'].queryset = event.payment_processors.filter(hidden=False)
    price = forms.ModelChoiceField(Price,required=True,empty_label=None,widget=forms.widgets.RadioSelect)
    payment_method = forms.ModelChoiceField(PaymentProcessor,required=True,empty_label=None,widget=forms.widgets.RadioSelect)

# class PriceForm(forms.ModelForm):
#     class Meta:
#         model=Price
#         fields=('name','description','amount','hidden')


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
    