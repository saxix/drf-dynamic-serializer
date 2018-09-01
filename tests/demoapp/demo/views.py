# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets

from dynamic_serializer.core import DynamicSerializerMixin, DynamicSerializer

logger = logging.getLogger(__name__)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        exclude = ('date_joined', 'password')


class BaseViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserSerializerShort(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class DynamicSerializerViewSet(DynamicSerializerMixin, BaseViewSet):
    serializers_fieldsets = {'light': ('last_name', 'first_name'),
                             'short': UserSerializerShort,
                             'broken': User,
                             'none': None,
                             'dynamic2': DynamicSerializer(UserSerializer),
                             'dynamic': DynamicSerializer(['first_name',
                                                           'last_name',
                                                           'is_active',
                                                           'email'
                                                           ])
                             }
