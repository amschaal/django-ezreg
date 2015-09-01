from django import forms

class DafisConfigurationForm(forms.Form):
    destination_dafis = forms.CharField(required=False)
    
class PaymentForm(forms.Form):
    dafis = forms.CharField(required=True)
    financial_contact = forms.CharField(required=True,widget=forms.widgets.Textarea)
    