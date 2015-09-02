from django import forms

class TouchnetConfigurationForm(forms.Form):
    production_url = forms.URLField(required=True)
    test_url = forms.URLField(required=True)
    fid = forms.CharField(max_length=5)
    upay_site_id = forms.IntegerField()
    posting_key = forms.CharField(max_length=50)



# TOUCHNET= {
#            'URL':'https://secure.touchnet.com:8443/C21642test_upay/web/index.jsp', 
#             'POSTING_KEY':'sdfaasfd',
#             'UPAY_SITE_ID': 1,
#            'FID':'006'
#            }
#     
class TouchnetPostForm(forms.Form):
    UPAY_SITE_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_LABEL = forms.CharField(widget=forms.HiddenInput())
    AMT = forms.CharField(widget=forms.HiddenInput)
    VALIDATION_KEY = forms.CharField(widget=forms.HiddenInput())
 
    