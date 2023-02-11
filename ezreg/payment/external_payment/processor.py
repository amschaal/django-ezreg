from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.external_payment.forms import PaymentForm, ExternalPaymentConfigurationForm

class ExternalPaymentProcessor(BasePaymentProcessor):
    id = 'external_payment_processor'
    name = 'External payment processor'
    exportable_fields = {'external_id':'External ID'}
    use_external_url = True
    @staticmethod
    def get_form(data=None, request=None):
        return PaymentForm
    @staticmethod
    def get_configuration_form():
        return ExternalPaymentConfigurationForm
    @staticmethod
    def post_process_form(payment, data):
        from ezreg.models import Registration, Payment
        payment.registration.status = Registration.STATUS_REGISTERED
        payment.status = Payment.STATUS_UNPAID
        payment.save()
        payment.registration.save()
    @staticmethod
    def get_additional_email_text(payment):
        return 'Please ensure that you have paid for your registration at {}.  Any unpaid registrations are subject to cancellation'.format(payment.registration.event.outside_url)
    