from django.urls import path, include
from rest_framework import routers
from .views import FolderViewSet

router = routers.DefaultRouter()
router.register(r'folders', FolderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
