from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.other_payment.forms import PaymentForm, OtherPaymentConfigurationForm

class OtherPaymentProcessor(BasePaymentProcessor):
    id = 'other_payment_processor'
    name = 'Other payment processor'
    exportable_fields = {'financial_contact':'Payment info'}
    @staticmethod
    def get_form(data=None, request=None):
        return PaymentForm
    @staticmethod
    def get_configuration_form():
        return OtherPaymentConfigurationForm
    @staticmethod
    def post_process_form(payment, data):
        from ezreg.models import Registration, Payment
        payment.registration.status = Registration.STATUS_REGISTERED
        payment.status = Payment.STATUS_PENDING
        payment.save()
        payment.registration.save()
    