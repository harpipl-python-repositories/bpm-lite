from rest_framework import serializers
from .models import Folder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['logical_id', 'name', 'description']


class BpmnUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    folder_name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
