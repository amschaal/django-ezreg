from django import forms
from django.forms.models import inlineformset_factory
from ezreg.models import Event, Price, Registration, PaymentProcessor
from django.forms import widgets
from tinymce.widgets import TinyMCE
from django.contrib.auth.models import Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from ezreg.payment import PaymentProcessors

class EventForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(EventForm,self).__init__(*args, **kwargs)
        self.fields['group'].queryset = user.groups.all()
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    cancellation_policy = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model=Event
        exclude = ('id',)

class PaymentProcessorForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PaymentProcessorForm,self).__init__(*args, **kwargs)
        self.fields['group'].queryset = user.groups.all()
        self.PaymentProcessors = PaymentProcessors()
        processor_choices = self.PaymentProcessors.get_choices()
        self.fields['processor_id'].widget = forms.widgets.Select(choices=processor_choices)
    class Meta:
        model= PaymentProcessor
        fields = ('processor_id','group','name','description','hidden')

class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event',None)
        super(RegistrationForm,self).__init__(*args, **kwargs)
    class Meta:
        model=Registration
        exclude = ('id','event','price')

class PriceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super(PriceForm,self).__init__(*args, **kwargs)
        self.fields['price'].queryset = event.prices.filter(hidden=False)
    price = forms.ModelChoiceField(Price,required=True,empty_label=None,widget=forms.widgets.RadioSelect)

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
        
        
    