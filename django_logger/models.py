from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Log(models.Model):
    PERMISSION_VIEW = 'VIEW_LOG'
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    @staticmethod
    def create(**kwargs):
        objects = kwargs.pop('objects',[])
        log = Log.objects.create(**kwargs)
        for o in objects:
            LogRelated.objects.create(log=log,content_object=o)
        return log
    @staticmethod
    def object_queryset(model_or_instance=None):
        kwargs = {}
        if model_or_instance:
            kwargs['content_type'] = ContentType.objects.get_for_model(model_or_instance)
            if hasattr(model_or_instance, 'pk'):
                kwargs['object_id'] = model_or_instance.pk
        return Log.objects.filter(**kwargs)

class LogRelated(models.Model):
    log = models.ForeignKey(Log,related_name='related_objects', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=25)
    content_object = GenericForeignKey('content_type', 'object_id')
