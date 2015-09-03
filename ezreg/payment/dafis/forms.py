from django import forms
from ezreg.payment.base import BasePaymentForm

class DafisConfigurationForm(forms.Form):
    destination_dafis = forms.CharField(required=False)
    
class PaymentForm(BasePaymentForm):
    dafis = forms.CharField(required=True)
    financial_contact = forms.CharField(required=True,widget=forms.widgets.Textarea)
    