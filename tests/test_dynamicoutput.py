# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

import pytest
from rest_framework.test import APIClient, APIRequestFactory

from demo.views import UserSerializer, DynamicOutputViewSet
from dynamic_serializer.core import SerializerStrategy, FieldsStrategy


@pytest.mark.django_db()
def test_default(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-output/', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == set(UserSerializer().fields.keys())


@pytest.mark.django_db()
def test_fields(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-output/?_fields=email,first_name,is_active', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'email', 'first_name', 'is_active'}


@pytest.mark.django_db()
def test_serializer(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-output/?serializer=light', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'first_name', 'last_name'}


@pytest.mark.django_db()
def test_priority(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-output/?_fields=first_name&serializer=short', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'first_name'}


@pytest.mark.django_db()
def test_custom_priority(admin_user, monkeypatch):
    class DummyViewSet(DynamicOutputViewSet):
        strategy_classes = [SerializerStrategy, FieldsStrategy]

    factory = APIRequestFactory()
    request = factory.get('/?_fields=first_name&serializer=short')
    view = DummyViewSet.as_view({'get': 'list'})
    response = view(request).render()  # Calling the view, not calling `.get()`

    j = json.loads(response.content.decode('utf8'))
    assert set(j[0].keys()) == {'email', 'first_name', 'last_name'}

    client = APIClient()
    response = client.get('/users-dynamic-output/?_fields=first_name&serializer=short', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'first_name'}
