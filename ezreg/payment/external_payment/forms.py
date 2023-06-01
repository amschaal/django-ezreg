from django import forms
from ezreg.payment.base import BasePaymentForm
from django.conf import settings

class ExternalPaymentConfigurationForm(forms.Form):
    require_external_id = forms.BooleanField(initial=False, required=False, help_text="Should a registrant be required to enter an external payment ID to complete registration?")
    external_id_text = forms.CharField(required=False
                                             ,initial="Please enter the external payment ID to confirm your registration."
                                             ,help_text="Enter the prompt for requesting an external payment ID.")
    confirm_text = forms.CharField(required=True,
                                   initial="Following registration, I will make payment using the designated link.  I understand that if payment is not made within 48 hours, my registration may be cancelled.",
                                   help_text="This text will appear next to the checkbox that must be checked in order to proceed.")
    
class PaymentForm(BasePaymentForm):
    external_id = forms.CharField(required=True)
    confirm = forms.BooleanField(required=True)
    def __init__(self,*args,**kwargs):
        super(PaymentForm, self).__init__(*args,**kwargs)
        self.fields['confirm'].label = self.config.get('confirm_text')
        if self.config.get('require_external_id'):
            self.fields['external_id'].label = self.config.get('external_id_text')
        else:
            del self.fields['external_id']