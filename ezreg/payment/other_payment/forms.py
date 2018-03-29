from django import forms
from ezreg.payment.base import BasePaymentForm
from django.conf import settings
import json
class OtherPaymentConfigurationForm(forms.Form):
    financial_contact_text = forms.CharField(required=True
                                             ,initial="Please enter contact information for the financial person that will be dealing with the check, wire transfer, etc."
                                             ,help_text="This will show up as help text during registration")
    confirm_text = forms.CharField(required=True,
                                   initial="I certify that I am not able to make payment by any other available method.",
                                   help_text="This text will appear next to the checkbox that must be checked in order to proceed.")#default="I certify that I am not able to make payment by any other available method."
    
class PaymentForm(BasePaymentForm):
    financial_contact = forms.CharField(required=True,widget=forms.widgets.Textarea)
    confirm = forms.BooleanField(required=True)
    def __init__(self,*args,**kwargs):
        super(PaymentForm, self).__init__(*args,**kwargs)
        self.fields['confirm'].label = self.config.get('confirm_text')
        self.fields['financial_contact'].label = self.config.get('financial_contact_text')
