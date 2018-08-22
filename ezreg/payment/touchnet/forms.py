from django import forms

class TouchnetConfigurationForm(forms.Form):
    FID = forms.CharField(max_length=5)
    FAU = forms.CharField(max_length=30,required=False)
    UPAY_SITE_ID = forms.IntegerField()
    POSTING_KEY = forms.CharField(max_length=50)
    UPAY_TEST_SITE_ID = forms.IntegerField()
    TEST_POSTING_KEY = forms.CharField(max_length=50)

class TouchnetPostForm(forms.Form):
    UPAY_SITE_ID = forms.CharField(widget=forms.HiddenInput())
    EXT_TRANS_ID = forms.CharField(widget=forms.HiddenInput())
#     EXT_TRANS_ID_LABEL = forms.CharField(widget=forms.HiddenInput())
    SUCCESS_LINK = forms.URLField(required=False,widget=forms.HiddenInput())
    CANCEL_LINK = forms.URLField(required=False,widget=forms.HiddenInput())
    AMT = forms.CharField(widget=forms.HiddenInput)
    VALIDATION_KEY = forms.CharField(widget=forms.HiddenInput())

