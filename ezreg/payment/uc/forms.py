from django import forms
from ezreg.payment.base import BasePaymentForm
from django.conf import settings
import re
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Div, HTML

# from ezreg.config import UC_PAYMENT_CONFIG
class UCConfigurationForm(forms.Form):
#     help_text = forms.CharField(required=False, help_text="If you'd like to override the help text under the \"Account information\" header, you may enter it here.")
    pass
    
UC_PAYMENT_CONFIG = {
    'UCB': {'name': 'UC Berkeley', 'regex': ['UCB_ACCOUNT$'], 'error_message':'Custom error message instead of default. Hint: "UCB_ACCOUNT" will validate.'},
    'UCSD': {'name': 'UC San Diego', 'regex': ['UCSD_ACCOUNT']}
}
class PaymentForm(BasePaymentForm):
    uc = forms.ChoiceField(required=True, label='Select UC', choices=[[k, v.get('name')] for k,v in UC_PAYMENT_CONFIG.items()])
    account = forms.CharField(required=True, help_text='Please enter the full UC account string.')
    financial_contact_first_name = forms.CharField(required=True, label="First Name")
    financial_contact_last_name = forms.CharField(required=True, label="Last Name")
    financial_contact_email = forms.EmailField(required=True, label="Email")
    financial_contact_phone = forms.CharField(required=True, label="Phone Number")
    pi_first_name = forms.CharField(required=True, label="First Name")
    pi_last_name = forms.CharField(required=True, label="Last Name")
    pi_email = forms.EmailField(required=True, label="Email")
    def __init__(self,*args,**kwargs):
        super(PaymentForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Account information',
                HTML(
                    '''<h4>Please select your university, and enter a full and valid UC account string.</h4>
                      <h4>Ask your financial contact or consult 
                      <a target="_blank" href="https://financeandbusiness.ucdavis.edu/finance/accounting-financial-reporting/intercampus/acct-strings">
                      https://financeandbusiness.ucdavis.edu/finance/accounting-financial-reporting/intercampus/acct-strings
                      </a> for details.</h4>
                    '''
                ),
                'uc',
                'account'
            ),
            Fieldset(
                'Financial contact',
                Div(
                    Div('financial_contact_first_name', css_class='col-xs-6'),
                    Div('financial_contact_last_name', css_class='col-xs-6'),
                    Div('financial_contact_email', css_class='col-xs-6'),
                    Div('financial_contact_phone', css_class='col-xs-6'),
                    css_class='row-fluid'
                )
            ),
            Fieldset(
                'PI',
                Div(
                    Div('pi_first_name', css_class='col-xs-6'),
                    Div('pi_last_name', css_class='col-xs-6'),
                    Div('pi_email', css_class='col-xs-6'),
                    css_class='row-fluid'
                )
            )
        )
    def clean(self):
        cleaned_data = super(PaymentForm, self).clean()
        uc = cleaned_data.get("uc")
        account = cleaned_data.get("account")
        config = UC_PAYMENT_CONFIG.get(uc)
        regex = config.get('regex', [])
        for r in regex:
            if re.match(r, account):
                return cleaned_data
        error_message = 'Invalid account string.  Please consult your financial contact or reference account string documentation for details on proper formatting.'
        error_message = config.get('error_message', error_message)
        raise forms.ValidationError({'account': error_message})
#         raise forms.ValidationError("The account is invalid.  Please ensure that chart, account, and (optionally) sub account refer to a valid account.")
#         return cleaned_data
            
