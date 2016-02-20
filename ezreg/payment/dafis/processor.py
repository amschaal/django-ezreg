from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.dafis.forms import DafisConfigurationForm, PaymentForm

class DafisPaymentProcessor(BasePaymentProcessor):
    id = 'dafis_payment_processor'
    name = 'UC Davis Account Processor'
    exportable_fields = {'account':'Account','sub_account':'Sub account','chart':'Chart','financial_contact':'Financial Contact'}
    @staticmethod
    def get_form(data=None, request=None):
        return PaymentForm
    @staticmethod
    def get_configuration_form():
        return DafisConfigurationForm
    @staticmethod
    def post_process_form(payment, data):
        from ezreg.models import Registration, Payment
        payment.registration.status = Registration.STATUS_REGISTERED
        payment.status = Payment.STATUS_PENDING
        payment.save()
        payment.registration.save()
    
#         BasePaymentProcessor.get_form(self, data, request)
    