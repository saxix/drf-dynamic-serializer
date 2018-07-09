from django.conf.urls import include, url
from rest_framework import routers

from .views import (DynamicFieldsSerializerViewSet, DynamicOutputViewSet,
                    DynamicSerializerViewSet)

router = routers.DefaultRouter()
router.register(r'users-dynamic', DynamicSerializerViewSet)
router.register(r'users-dynamic-fields', DynamicFieldsSerializerViewSet)
router.register(r'users-dynamic-output', DynamicOutputViewSet)

urlpatterns = (
    url(r'^', include(router.urls)),
)
