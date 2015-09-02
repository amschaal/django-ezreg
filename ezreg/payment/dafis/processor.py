from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.dafis.forms import DafisConfigurationForm, PaymentForm

class DafisPaymentProcessor(BasePaymentProcessor):
    id = 'dafis_payment_processor'
    name = 'UC Davis Account Processor'
    @staticmethod
    def get_form(data=None, request=None):
        return PaymentForm
    @staticmethod
    def get_configuration_form():
        return DafisConfigurationForm
    
#         BasePaymentProcessor.get_form(self, data, request)
    