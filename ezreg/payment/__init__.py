from django.conf import settings
from django.utils.module_loading import import_string
class PaymentProcessors:
    def __init__(self):
        processors = getattr(settings,'PAYMENT_PROCESSORS')
        self.payment_processors = {}    
        for processor in processors:
            p = import_string(processor)
            self.payment_processors[p.id]=p
    def get_processor(self,id):
        if self.payment_processors.has_key(id):
            return self.payment_processors[id]
        return None
    def get_choices(self):
        choices = ()
        for id, processor in self.payment_processors.iteritems():
            choices += ((id,processor.name),)
        return choices
        