class BasePaymentProcessor:
    id = 'base_payment_processor'
    name = 'Base Payment Processor'
    def get_form(self,data,request):
        raise NotImplementedError("get_form is not implemented for this payment processor")
    