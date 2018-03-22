from django.core import validators
from django.db import models


class EmailListField(models.CharField):
#     __metaclass__ = models.SubfieldBase

    class EmailListValidator(validators.EmailValidator):
        def __call__(self, value):
            for email in value:
                super(EmailListField.EmailListValidator, self).__call__(email)

    class Presentation(list):

        def __unicode__(self):
            return u", ".join(self)

        def __str__(self):
            return ", ".join(self)

    default_validators = [EmailListValidator()]

    def get_db_prep_value(self, value, *args, **kwargs):
        if not value:
            return
        if isinstance(value,list):
            return ','.join(unicode(s) for s in value)
        return value
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def to_python(self, value):
        if not value:
            return
        if isinstance(value, self.Presentation):
            return value
        return self.Presentation([address.strip() for address in value.split(',')])