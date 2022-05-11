# from django.conf.urls import  url
from ezreg.payment.touchnet import views
from django.urls.conf import re_path
urlpatterns = [
    re_path(r'^touchnet/postback/', views.postback,name='touchnet_postback'),
]
