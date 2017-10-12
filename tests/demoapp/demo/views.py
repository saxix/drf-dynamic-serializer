# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets

from dynamic_serializer.core import DynamicSerializerMixin

logger = logging.getLogger(__name__)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        exclude = ('date_joined', 'password')


class UserSerializerShort(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class UserViewSet(DynamicSerializerMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializers_fieldsets = {'light': ('last_name', 'first_name'),
                             'short': UserSerializerShort,
                             'broken': User,
                             'none': None,
                             }
