from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.dafis.forms import DafisConfigurationForm, PaymentForm

class DafisPaymentProcessor(BasePaymentProcessor):
    id = 'dafis_payment_processor'
    name = 'UC Davis Account Processor'
    def get_form(self, data, request):
        return PaymentForm
    def get_configuration_form(self):
        return DafisConfigurationForm
    
#         BasePaymentProcessor.get_form(self, data, request)
    