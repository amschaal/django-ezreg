from rest_framework import viewsets
from django_logger.models import Log
from django_logger.api.serializers import LogSerializer
from rest_framework.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType

class LogViewset(viewsets.ReadOnlyModelViewSet):
    model = Log
    serializer_class = LogSerializer
    filter_fields = {'text':['icontains']}
    ordering_fields = ('created','text')
    def get_queryset(self):
        content_type = self.request.query_params.get('content_type',None)
        object_id = self.request.query_params.get('object_id',None)
        if not self.request.user.is_superuser:
            if not content_type or not object_id:
                raise PermissionDenied('You must provide a content_type and object_id argument unless you are a super admin')
            else:
                ct = ContentType.objects.get_for_id(content_type)
                obj = ct.get_object_for_this_type(pk=object_id)
                if hasattr(obj, 'has_permission') and not obj.has_permission(self.request.user,Log.PERMISSION_VIEW):
                    raise PermissionDenied('You do not have permission to view these logs')
        filters = {}
        if content_type:
            filters['related_objects__content_type']=content_type
        if object_id:
            filters['related_objects__object_id']=object_id
        return Log.objects.filter(**filters) 
