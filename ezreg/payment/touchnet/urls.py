from django.conf.urls import  url

urlpatterns = [
    url(r'^touchnet/postback/', 'ezreg.payment.touchnet.views.postback',name='touchnet_postback'),
]
