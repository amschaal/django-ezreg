"""ezreg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers

from ezreg.api.views import PriceViewset, PaymentProcessorViewset, \
    EventPageViewset, RegistrationViewset, MailerMessageViewset
from ezreg.registration import RegistrationWizard


router = routers.DefaultRouter()
router.register(r'prices', PriceViewset)
router.register(r'payment_processors', PaymentProcessorViewset)
router.register(r'event_pages', EventPageViewset)
router.register(r'registrations', RegistrationViewset)
router.register(r'emails', MailerMessageViewset)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'ezreg.views.home',name='home'),
    url(r'^events/$', 'ezreg.views.events',name='events'),
    url(r'^events/create/$', 'ezreg.views.create_modify_event',name='create_event'),
    url(r'^events/(?P<id>[A-Z0-9]{10})/modify/$', 'ezreg.views.create_modify_event',name='modify_event'),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/$', 'ezreg.views.event',name='event'),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/page/(?P<page_slug>[\w-]+)/$', 'ezreg.views.event_page',name='event_page'),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/register/$', RegistrationWizard.as_view(), name="register",kwargs={'waitlist':False}),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/waitlist/$', RegistrationWizard.as_view(), name="waitlist",kwargs={'waitlist':True}),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/apply/$', RegistrationWizard.as_view(), name="apply",kwargs={'apply':True}),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/complete_registration/(?P<registration_id>[A-Za-z0-9_\-]{10})/$', RegistrationWizard.as_view(), name="complete_registration",kwargs={'complete':True}),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/registrations/$', 'ezreg.views.registrations', name="registrations"),
    url(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{5,100})/emails/$', 'ezreg.views.event_emails', name="event_emails"),
    url(r'^events/(?P<event_id>[A-Za-z0-9_\-]{5,100})/update_statuses/$', 'ezreg.api.views.update_event_statuses', name="update_event_statuses"),
    url(r'^events/(?P<event_id>[A-Za-z0-9_\-]{5,100})/send_event_emails/$', 'ezreg.api.views.send_event_emails', name="send_event_emails"),
    
    url(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/$', 'ezreg.views.registration', name="registration"),
    url(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/modify/$', 'ezreg.views.modify_registration', name="modify_registration"),
    url(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/update_status/$', 'ezreg.views.update_registration_status', name="update_registration_status"),
    url(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/pay/$', 'ezreg.views.pay', name="pay"),
    url(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/invite.ics$', 'ezreg.views.registration_ical', name="registration_ical"),
    url(r'^payment_processors/$', 'ezreg.views.payment_processors',name='payment_processors'),
    url(r'^payment_processors/create/$', 'ezreg.views.create_modify_payment_processor',name='create_payment_processor'),
    url(r'^payment_processors/(?P<id>\d+)/modify/$', 'ezreg.views.create_modify_payment_processor',name='modify_payment_processor'),
    url(r'^payment_processors/(?P<id>\d+)/configure/$', 'ezreg.views.configure_payment_processor',name='configure_payment_processor'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^api/', include(router.urls)),
    url(r'^jsurls.js$', 'ezreg.jsutils.jsurls', {}, 'jsurls'), 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
