# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework.test import APIRequestFactory

from demo.views import BaseViewSet, DynamicSerializerViewSet
from dynamic_serializer.core import serializer_factory, SerializerStrategy


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
def test_dynamicserializermixin():
    # v = BaseViewSet()
    # vs = DynamicSerializerViewSet()
    factory = APIRequestFactory()
    request = factory.get('/?_fields=first_name&serializer=short')
    view = DynamicSerializerViewSet.as_view({'get': 'list'})(request)
    # response = view(request).render()  # Calling the view, not calling `.get()`
    # vs.request = request
    # s = SerializerStrategy(view)
    #
    # FIXME: remove me
    # print(111, s._get_serializer_from_param())


