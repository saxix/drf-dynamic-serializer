# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

from demo.views import BaseViewSet, DynamicSerializerViewSet
from dynamic_serializer.core import serializer_factory


def test_serializer_factory():
    from django.contrib.auth.models import User
    s = serializer_factory(User)
    assert s

    s = serializer_factory(User, fields=["username"])
    assert list(s().fields.keys()) == ['username']

    s = serializer_factory(User, exclude=['id', 'password',
                                          'last_login', 'is_superuser', 'first_name',
                                          'last_name', 'email', 'is_staff', 'is_active',
                                          'date_joined', 'groups', 'user_permissions'])
    assert list(s().fields.keys()) == ['username']


@pytest.mark.django_db
def test_get_serializer_fields():
    vs = DynamicSerializerViewSet()
    assert vs.get_serializer_fields('light') == ['first_name', 'last_name']
    assert vs.get_serializer_fields('std') == ['email',
                                               'first_name',
                                               'groups',
                                               'is_active',
                                               'is_staff',
                                               'is_superuser',
                                               'last_login',
                                               'last_name',
                                               'url',
                                               'user_permissions',
                                               'username']
