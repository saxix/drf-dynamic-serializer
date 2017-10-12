# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from django.contrib.admin import ModelAdmin, register
from .models import DemoModel


@register(DemoModel)
class DemoAdmin(ModelAdmin):
    pass
