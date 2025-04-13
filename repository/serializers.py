from rest_framework import serializers
from .models import Folder

class FolderSerializer(serializers.ModelSerializer):
    logicalId = serializers.UUIDField(source='logical_id', read_only=True)
    
    class Meta:
        model = Folder
        fields = ['logicalId', 'name', 'description']
        read_only_fields = ['logicalId']