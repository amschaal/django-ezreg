class BasePaymentProcessor:
    id = 'base_payment_processor'
    name = 'Base Payment Processor'
    def __init__(self,config):
        self.config = config
    @staticmethod
    def get_form():
        return None
    @staticmethod
    def get_post_form(payment):
        return None
        
#         raise NotImplementedError("get_form is not implemented for this payment processor")
    