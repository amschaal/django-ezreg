from django import forms
class BasePaymentProcessor:
    id = 'base_payment_processor'
    name = 'Base Payment Processor'
    payment_template = 'ezreg/pay.html'
    def __init__(self,config):
        self.config = config
    @staticmethod
    def get_form():
        return None
    @staticmethod
    def process_form(event, data):
        pass
    @staticmethod
    def post_process_form(payment, data):
        pass
    @staticmethod
    def get_post_form(payment):
        return None

class BasePaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super(BasePaymentForm,self).__init__(*args, **kwargs)
    template = 'ezreg/registration/payment.html'
#         raise NotImplementedError("get_form is not implemented for this payment processor")
    