from django import forms

class TouchnetConfigurationForm(forms.Form):
    FID = forms.CharField(max_length=5)
    UPAY_SITE_ID = forms.IntegerField()
    POSTING_KEY = forms.CharField(max_length=50)
    UPAY_TEST_SITE_ID = forms.IntegerField()
    TEST_POSTING_KEY = forms.CharField(max_length=50)

class TouchnetPostForm(forms.Form):
    UPAY_SITE_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_LABEL = forms.CharField(widget=forms.HiddenInput())
    AMT = forms.CharField(widget=forms.HiddenInput)
    VALIDATION_KEY = forms.CharField(widget=forms.HiddenInput())
 
    
