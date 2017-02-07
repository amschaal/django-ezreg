from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.touchnet.forms import TouchnetConfigurationForm, TouchnetPostForm
from django.conf import settings
from django.core.urlresolvers import reverse
class TouchnetPaymentProcessor(BasePaymentProcessor):
    id = 'touchnet_payment_processor'
    name = 'Touchnet Payment Processor'
    payment_template = 'touchnet/pay.html'
    @staticmethod
    def get_configuration_form():
        return TouchnetConfigurationForm
    @staticmethod
    def get_post_form(payment):
        conf = payment.processor.config
        import base64
        import hashlib
        m = hashlib.md5()
        #https://secure.touchnet.com:8443/C21642test_upay/web/index.jsp
        site_id = TouchnetPaymentProcessor.get_site_id(payment)
        posting_key = TouchnetPaymentProcessor.get_posting_key(payment)
        data = {'UPAY_SITE_ID':site_id,
                'EXT_TRANS_ID':'FID=%s;%s'%(conf['FID'],payment.registration.id) if not conf.get('FAU') else 'FID=%s;FAU=%s;%s'%(conf['FID'],conf['FAU'],payment.registration.id),
#                 'EXT_TRANS_ID_LABEL':payment.registration.event.title,
                'SUCCESS_LINK': settings.SITE_URL + reverse('registration',kwargs={'id':payment.registration.id}),
                'CANCEL_LINK': settings.SITE_URL + reverse('event',kwargs={'slug_or_id':payment.registration.event.slug_or_id}),
                'AMT': payment.amount
                }
        m.update(posting_key+data['EXT_TRANS_ID']+str(data['AMT']))
        data['VALIDATION_KEY']=base64.encodestring(m.digest())
        form = TouchnetPostForm(initial=data)
        form.action = settings.TOUCHNET_TEST_URL if payment.registration.test else settings.TOUCHNET_PRODUCTION_URL
        return form
    @staticmethod
    def get_site_id(payment):
        return payment.processor.config['UPAY_TEST_SITE_ID'] if payment.registration.test else payment.processor.config['UPAY_SITE_ID']
    @staticmethod
    def get_posting_key(payment):
        return payment.processor.config['TEST_POSTING_KEY'] if payment.registration.test else payment.processor.config['POSTING_KEY']
