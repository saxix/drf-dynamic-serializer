# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework.test import APIClient

from demo.views import UserSerializer


@pytest.mark.django_db()
def test_serializer_default(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-fields/', format='json')
    assert response.status_code == 200
    # assert response.json() == [{'username': admin_user.username}]
    assert set(response.json()[0].keys()) == set(UserSerializer().fields.keys())


@pytest.mark.django_db()
def test_fields(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-fields/?_fields=email,first_name,is_active', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'email', 'first_name', 'is_active'}


@pytest.mark.django_db()
def test_not_allowed_field(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-fields/?_fields=password,first_name', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'first_name'}


@pytest.mark.django_db()
def test_not_existing_field(admin_user):
    client = APIClient()
    response = client.get('/users-dynamic-fields/?_fields=asd,first_name', format='json')
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == {'first_name'}
