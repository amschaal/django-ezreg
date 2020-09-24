from ezreg.payment.base import BasePaymentProcessor
from ezreg.payment.uc.forms import PaymentForm, UCConfigurationForm
from collections import OrderedDict

class UCPaymentProcessor(BasePaymentProcessor):
    id = 'uc_payment_processor'
    name = 'UC Account String Processor'
    exportable_fields = OrderedDict([('uc','UC'),('account','Account'),('financial_contact_first_name','Financial Contact First Name'),('financial_contact_last_name','Financial Contact Last Name'),('financial_contact_email','Financial Contact Email'),('pi_first_name','PI First Name'),('pi_last_name','PI Last Name'),('pi_email','PI Email')])
    @staticmethod
    def get_form(data=None, request=None):
        return PaymentForm
    @staticmethod
    def get_configuration_form():
        return UCConfigurationForm
    @staticmethod
    def post_process_form(payment, data):
        from ezreg.models import Registration, Payment
        payment.registration.status = Registration.STATUS_REGISTERED
        payment.status = Payment.STATUS_PENDING
        payment.save()
        payment.registration.save()
    
#         BasePaymentProcessor.get_form(self, data, request)
    