# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import logging
from django.db import models

logger = logging.getLogger(__name__)


class DemoModel(models.Model):
    class Meta:
        ordering = ("id",)
