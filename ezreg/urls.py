"""ezreg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers
from django_json_forms import urls as json_form_urls
from ezreg import views
from ezreg.api import views as api_views
from cas import views as cas_views
# from ezreg.jsutils import jsurls
from ezreg.api.views import PriceViewset, PaymentProcessorViewset, \
    EventPageViewset, RegistrationViewset, MailerMessageViewset, EventViewset,\
    RefundViewset
from ezreg.registration import RegistrationWizard
from django_logger.api.views import LogViewset
from ezreg.feeds import EventsFeed, UpcomingEventsFeed, PastEventsFeed
from django.urls.conf import re_path, path


router = routers.DefaultRouter()
router.register(r'prices', PriceViewset, 'Price')
router.register(r'payment_processors', PaymentProcessorViewset, 'PaymentProcessor')
router.register(r'event_pages', EventPageViewset, 'EventPage')
router.register(r'events', EventViewset, 'Event')
router.register(r'registrations', RegistrationViewset, 'Registration')
router.register(r'emails', MailerMessageViewset, 'Email')
router.register(r'logs', LogViewset, 'Log')
router.register(r'refunds', RefundViewset, 'Refund')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', views.home, name='home'),
    re_path(r'^events/organizer/(?P<organizer_slug>[A-Za-z0-9_\-]{3,})/$', views.home, name='organizer_events'),
    re_path(r'^events/upcoming/$', views.events, name='upcoming_events',kwargs={'page':'upcoming'}),
    re_path(r'^events/past/$', views.events, name='past_events',kwargs={'page':'past'}),
    re_path(r'^manage_events/$', views.manage_events, name='manage_events'),
    re_path(r'^manage_events/revenue/$', views.export_event_revenue, name='export_event_revenue'),
    re_path(r'^registrations/$', views.registration_search, name='registration_search'),
    re_path(r'^events/create/$', views.create_event, name='create_event'),
    re_path(r'^events/(?P<event>[A-Z0-9]{10})/manage/$', views.manage_event, name='manage_event'),
    re_path(r'^events/(?P<event>[A-Z0-9]{10})/copy/$', views.copy_event, name='copy_event'),
    re_path(r'^events/(?P<event>[A-Z0-9]{10})/delete/$', views.delete_event, name='delete_event'),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/$', views.event, name='event'),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/page/(?P<page_slug>[\w-]+)/$', views.event_page, name='event_page'),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/register/$', RegistrationWizard.as_view(), name="register",kwargs={'waitlist':False,'register':True}),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/waitlist/$', RegistrationWizard.as_view(), name="waitlist",kwargs={'waitlist':True}),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/apply/$', RegistrationWizard.as_view(), name="apply",kwargs={'apply':True}),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/admin/register/$', RegistrationWizard.as_view(), name="admin_register",kwargs={'waitlist':False,'register':True,'admin':True}),
    re_path(r'^events/(?P<slug_or_id>[A-Za-z0-9_\-]{3,100})/complete_registration/(?P<registration_id>[A-Za-z0-9_\-]{10})/$', RegistrationWizard.as_view(), name="complete_registration",kwargs={'complete':True}),
    re_path(r'^events/(?P<event>[A-Za-z0-9_\-]{3,100})/update_statuses/$', api_views.update_event_statuses, name="update_event_statuses"),
    re_path(r'^events/(?P<event>[A-Za-z0-9_\-]{3,100})/export_registrations/$', views.export_registrations, name="export_registrations"),
    re_path(r'^events/(?P<event>[A-Za-z0-9_\-]{3,100})/update_event_form/$', api_views.update_event_form, name="update_event_form"),
    re_path(r'^events/(?P<event>[A-Za-z0-9_\-]{3,100})/send_event_emails/$', api_views.send_event_emails, name="send_event_emails"),
    
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/$', views.registration, name="registration"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/cancel/$', views.cancel_registration, name="cancel_registration"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/modify/$', views.modify_registration, name="modify_registration"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/modify_payment/$', views.modify_payment, name="modify_payment"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/update_status/$', views.update_registration_status, name="update_registration_status"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/request_refund/$', views.request_refund, name="request_refund"),
    re_path(r'^registrations/(?P<id>[A-Za-z0-9_\-]{10})/pay/$', views.pay, name="pay"),
    re_path(r'^refunds/pending/$', views.pending_refunds, name='pending_refunds'),
    re_path(r'^payment_processors/$', views.payment_processors, name='payment_processors'),
    re_path(r'^payment_processors/create/$', views.create_payment_processor, name='create_payment_processor'),
    re_path(r'^payment_processors/(?P<id>\d+)/modify/$', views.modify_payment_processor, name='modify_payment_processor'),
    re_path(r'^payment_processors/(?P<id>\d+)/configure/$', views.configure_payment_processor, name='configure_payment_processor'),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^api/', include(router.urls)),
    re_path(r'^api/events/(?P<event>[A-Za-z0-9_\-]{10})/payment_processors/$', api_views.event_payment_processors, name="event_payment_processors"),
    re_path(r'^api/events/(?P<event>[A-Za-z0-9_\-]{10})/export_registrations/$', api_views.export_registrations, name="api_export_registrations"),
    #RSS Feed
    re_path(r'^feeds/events/all/(?P<organizer_slug>[A-Za-z0-9_\-]{3,})/rss/$', EventsFeed()),
    re_path(r'^feeds/events/upcoming/(?P<organizer_slug>[A-Za-z0-9_\-]{3,})/rss/$', UpcomingEventsFeed()),
    re_path(r'^feeds/events/past/(?P<organizer_slug>[A-Za-z0-9_\-]{3,})/rss/$', PastEventsFeed()),
    re_path(r'^json_forms/', include(json_form_urls.urlpatterns)),
#     re_path(r'^jsurls.js$', jsurls, {}, 'jsurls'), 
    # CAS
    re_path(r'^accounts/login/$', cas_views.login, name='login'),
    re_path(r'^accounts/logout/$', cas_views.logout, name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.utils.importlib import import_module
#@todo: do something cleaner than this...
if hasattr(settings, 'PAYMENT_PROCESSOR_URLS'):
    for processor_urls in settings.PAYMENT_PROCESSOR_URLS:
        try:
#             mod = import_module(processor_urls)
            urlpatterns += [re_path(r'^processors/',include(processor_urls))]
        except Exception as e:
            print(e) 

handler403 = 'ezreg.error_views.handler403'
