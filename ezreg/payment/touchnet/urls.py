from django.conf.urls import  url
from ezreg.payment.touchnet import views
urlpatterns = [
    url(r'^touchnet/postback/', views.postback,name='touchnet_postback'),
]
