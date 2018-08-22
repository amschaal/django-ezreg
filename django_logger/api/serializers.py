from rest_framework import serializers
from django_logger.models import Log


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        exclude = ()