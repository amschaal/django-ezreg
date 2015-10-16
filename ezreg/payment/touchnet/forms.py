from django import forms

class TouchnetConfigurationForm(forms.Form):
    fid = forms.CharField(max_length=5)
    upay_site_id = forms.IntegerField()
    posting_key = forms.CharField(max_length=50)

class TouchnetPostForm(forms.Form):
    UPAY_SITE_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_LABEL = forms.CharField(widget=forms.HiddenInput())
    AMT = forms.CharField(widget=forms.HiddenInput)
    VALIDATION_KEY = forms.CharField(widget=forms.HiddenInput())
 
    