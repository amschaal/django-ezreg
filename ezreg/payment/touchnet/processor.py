from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.touchnet.forms import TouchnetConfigurationForm, TouchnetPostForm
from django.conf import settings
class TouchnetPaymentProcessor(BasePaymentProcessor):
    id = 'touchnet_payment_processor'
    name = 'Touchnet Payment Processor'
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
        data = {'UPAY_SITE_ID':conf['upay_site_id'],
                'EXT_TRANS_ID':'FID=%s;%d;'%(conf['fid'],payment.id),
                'EXT_TRANS_ID_LABEL':'%s services'%payment.registration.event.title,
                'AMT': payment.amount
                }
        m.update(conf['posting_key']+data['EXT_TRANS_ID']+str(data['AMT']))
        data['VALIDATION_KEY']=base64.encodestring(m.digest())
        form = TouchnetPostForm(initial=data)
        form.action = settings.TOUCHNET_TEST_URL if payment.registration.test else settings.TOUCHNET_PRODUCTION_URL
        return form
    