from django import forms
from ezreg.payment.base import BasePaymentForm
from django.conf import settings
import json
import urllib2
from ezreg.config import KFS_CHART_OPTIONS
class DafisConfigurationForm(forms.Form):
    destination_dafis = forms.CharField(required=False)
    
class PaymentForm(BasePaymentForm):
    chart = forms.CharField(max_length=3,required=True)
    account = forms.CharField(required=True,help_text='Account will be charged the week of the event')
    sub_account = forms.CharField(required=False)
    financial_contact = forms.CharField(required=True,widget=forms.widgets.Textarea)
    def __init__(self,*args,**kwargs):
        #IE: KFS_CHART_OPTIONS = (('3','3 - UC Davis'),('s','s - UC Davis School of Medicine'))
        if hasattr(settings, 'KFS_CHART_OPTIONS'):
            super(PaymentForm,self).__init__(*args,**kwargs)
        self.fields['chart'].widget = forms.Select(choices=settings.KFS_CHART_OPTIONS)
    def clean(self):
        cleaned_data = super(PaymentForm, self).clean()
        chart = cleaned_data.get("chart")
        account = cleaned_data.get("account")
        sub_account = cleaned_data.get("sub_account")
        URL = None
        if sub_account and chart and account:
            if hasattr(settings, 'KFS_VALIDATE_SUBACCOUNT_URL'):
                URL = settings.KFS_VALIDATE_SUBACCOUNT_URL % (chart,account,sub_account)
#             URL = "https://kfs.ucdavis.edu/kfs-prd/remoting/rest/fau/subaccount/%s/%s/%s/isvalid" % (chart,account,sub_account)
        elif chart and account:
            if hasattr(settings, 'KFS_VALIDATE_ACCOUNT_URL'):
                URL = settings.KFS_VALIDATE_ACCOUNT_URL % (chart,account)
#             URL = "https://kfs.ucdavis.edu/kfs-prd/remoting/rest/fau/account/%s/%s/isvalid" % (chart,account)
        valid = None
        if URL:
            try:
                valid = json.load(urllib2.urlopen(URL))
                cleaned_data['validated']=valid
            except Exception, e:
                valid = True
                cleaned_data['validated']=valid # If request fails, don't hold up registration
            if valid != True:
                raise forms.ValidationError("The account is invalid.  Please ensure that chart, account, and (optionally) sub account refer to a valid account.")
        return cleaned_data
            
                
# import json
# import urllib2
# URL = "https://kfs.ucdavis.edu/kfs-prd/remoting/rest/fau/account/3/FL16042/isvalid"
# print json.load(urllib2.urlopen(URL))
