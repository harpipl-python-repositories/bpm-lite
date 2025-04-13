from django.shortcuts import render
from rest_framework import viewsets
from .models import Folder
from .serializers import FolderSerializer

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    lookup_field = 'logical_id'
    lookup_url_kwarg = 'logical_id'
