# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from factory import DjangoModelFactory


class UserFactory():
    class Meta:
        model = User

    first_name = 'John'
    last_name = 'Doe'
    admin = False


class AdminFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'Admin'
    last_name = 'User'
    admin = True
