from django import forms
from ezreg.payment.base import BasePaymentForm
from django.conf import settings
import json
import urllib2
class DafisConfigurationForm(forms.Form):
    destination_dafis = forms.CharField(required=False)
    
class PaymentForm(BasePaymentForm):
    chart = forms.CharField(max_length=3,required=True)
    account = forms.CharField(required=True)
    sub_account = forms.CharField(required=False)
    financial_contact = forms.CharField(required=True,widget=forms.widgets.Textarea)
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
        if URL:
            try:
                valid = json.load(urllib2.urlopen(URL))
                cleaned_data['validated']=True
            except Exception, e:
                valid = False
                cleaned_data['validated']=False
            if not valid:
                raise forms.ValidationError("The account is invalid.  Please ensure that chart, account, and (optionally) sub account refer to a valid account.")
                
            
                
            
                
# import json
# import urllib2
# URL = "https://kfs.ucdavis.edu/kfs-prd/remoting/rest/fau/account/3/FL16042/isvalid"
# print json.load(urllib2.urlopen(URL))