from rest_framework import serializers
from ezreg.models import Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('id','event','name','amount','description','hidden')
        
        
        
# class ProjectSerializer(serializers.ModelSerializer):
#     lab__name = serializers.Field(source='lab.name')
#     type = serializers.RelatedField(many=False)
#     data = JSONWritableField()
#     class Meta:
#         model = Project
#         fields = ('id','name','type','description','lab','lab__name','data')