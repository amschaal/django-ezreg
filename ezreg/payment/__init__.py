from django.conf import settings
from django.utils.module_loading import import_string
class PaymentProcessorManager:
    def __init__(self):
        processors = getattr(settings,'PAYMENT_PROCESSORS')
        self.payment_processors = {}    
        for processor in processors:
            p = import_string(processor)
            self.payment_processors[p.id]=p
    def get_processor(self,id):
        if id in self.payment_processors:
            return self.payment_processors[id]
        return None
    def get_choices(self):
        choices = ()
        for id, processor in self.payment_processors.items():
            choices += ((id,processor.name),)
        return choices
        