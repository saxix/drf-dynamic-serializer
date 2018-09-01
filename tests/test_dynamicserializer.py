# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from urllib.parse import quote

import pytest
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.test import APIClient, APIRequestFactory

from demo.views import UserSerializer, UserSerializerShort
from dynamic_serializer.core import InvalidSerializerError, DynamicSerializerMixin, InvalidFieldError


@pytest.mark.django_db()
def test_serializer_default(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic/', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == set(UserSerializer().fields.keys())


@pytest.mark.django_db()
def test_serializer_standard(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic/?%2Bserializer=std', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'email', 'first_name',
                                              'groups', 'is_active',
                                              'is_staff', 'last_login',
                                              'user_permissions', 'url',
                                              'last_name', 'is_superuser',
                                              'username'}


@pytest.mark.django_db()
def test_serializer_light(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic/?%2Bserializer=light', format='json')
    assert set(response.json()[0].keys()) == {'first_name', 'last_name'}


@pytest.mark.django_db()
def test_serializer_short(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic/?%2Bserializer=short', format='json')
    assert set(response.json()[0].keys()) == {'email', 'first_name', 'last_name'}


@pytest.mark.django_db()
def test_serializer_broken(admin_user):
    client = APIClient()
    with pytest.raises(InvalidSerializerError):
        client.get('/users-dynamic/?%2Bserializer=broken', format='json')


@pytest.mark.django_db()
def test_serializer_wrong(admin_user):
    client = APIClient()
    with pytest.raises(InvalidSerializerError):
        client.get('/users-dynamic/?%2Bserializer=wrong', format='json')


@pytest.mark.django_db()
def test_serializer_none(admin_user):
    client = APIClient()
    with pytest.raises(InvalidSerializerError):
        client.get('/users-dynamic/?%2Bserializer=none', format='json')


@pytest.mark.django_db()
def test_serializer_dynamic(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic/?%2Bserializer=dynamic&%2Bfields=first_name,is_active', format='json')
    assert set(response.json()[0].keys()) == {'first_name', 'is_active'}

    response = client.get('/users-dynamic/?%2Bserializer=dynamic&%2Bfields=is_active', format='json')
    assert set(response.json()[0].keys()) == {'is_active'}

    response = client.get('/users-dynamic/?%2Bserializer=dynamic2&%2Bfields=is_active', format='json')
    assert set(response.json()[0].keys()) == {'is_active'}

    with pytest.raises(InvalidFieldError) as e:
        client.get('/users-dynamic/?%2Bserializer=dynamic&%2Bfields=invalid', format='json')
        assert str(e) == "invalid"


@pytest.mark.django_db()
def test_missing_queryset(admin_user):
    class DummyViewSet(DynamicSerializerMixin, viewsets.ModelViewSet):
        serializer_class = UserSerializer
        serializers_fieldsets = {'light': ('last_name', 'first_name'),
                                 'short': UserSerializerShort,
                                 'none': None,
                                 }
        queryset = None

    factory = APIRequestFactory()
    request = factory.get('/?uuid=abcd')
    view = DummyViewSet.as_view({'get': 'list'})
    with pytest.raises(AssertionError):
        view(request)  # Calling the view, not calling `.get()`


@pytest.mark.django_db()
def test_no_serializers_fieldsets(admin_user, monkeypatch):
    class DummyViewSet(DynamicSerializerMixin, viewsets.ModelViewSet):
        serializer_class = UserSerializer
        queryset = User.objects.all()

    factory = APIRequestFactory()
    request = factory.get('/?uuid=abcd')
    view = DummyViewSet.as_view({'get': 'list'})
    response = view(request).render()  # Calling the view, not calling `.get()`

    j = json.loads(response.content.decode('utf8'))
    assert set(j[0].keys()) == {'email', 'first_name',
                                'groups', 'is_active',
                                'is_staff', 'last_login',
                                'user_permissions', 'url',
                                'last_name', 'is_superuser',
                                'username'}
