# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from inspect import isclass
from urllib.parse import unquote, quote

from rest_framework.serializers import BaseSerializer, ModelSerializer

logger = logging.getLogger(__name__)

NOTSET = object()


def serializer_factory(model, base=ModelSerializer, fields=NOTSET, exclude=NOTSET):
    attrs = {'model': model}
    if fields != NOTSET:
        attrs['fields'] = fields
    if exclude != NOTSET:
        attrs['exclude'] = exclude

    parent = (object,)
    if hasattr(base, 'Meta'):
        parent = (base.Meta,)

    Meta = type('Meta', parent, attrs)
    class_name = model.__name__ + 'Serializer'
    return type(base)(class_name, (base,), {'Meta': Meta, })


class InvalidSerializerError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


def get_attr(obj, attr, default=None):
    """Recursive get object's attribute. May use dot notation.

    >>> class C(object): pass
    >>> a = C()
    >>> a.b = C()
    >>> a.b.c = 4
    >>> get_attr(a, 'b.c')
    4

    >>> get_attr(a, 'b.c.y', None)

    >>> get_attr(a, 'b.c.y', 1)
    1
    """
    if '.' not in attr:
        return getattr(obj, attr, default)
    else:
        L = attr.split('.')
        return get_attr(getattr(obj, L[0], default), '.'.join(L[1:]), default)


class DynamicSerializer(object):
    def __init__(self, allowed_fields):
        if isinstance(allowed_fields, (list, tuple, set)):
            self.allowed_fields = set(allowed_fields)
        else:
            self.allowed_fields = {f for f in allowed_fields().get_fields()}

    def get_fields(self, view):
        requested_fields = set(view.request.query_params.get(view.dynamic_fields_param, '').split(','))
        if requested_fields - self.allowed_fields:
            raise InvalidFieldError(",".join(requested_fields - self.allowed_fields))

        return requested_fields


class DynamicSerializerMixin(object):
    serializer_field_param = '+serializer'
    dynamic_fields_param = '+fields'
    serializers_fieldsets = {'std': None}
    _serializers_classes = {}

    def get_serializer_fields(self, name):
        target = self.serializers_fieldsets.get(name, None)
        if isinstance(target, (list, tuple)):
            fields = target
        else:
            ser = self._get_serializer_from_param(name)
            return sorted([f for f in ser().get_fields()])
        return sorted(fields)

    @property
    def _default_serializer(self):
        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()

        if not issubclass(serializer_class, BaseSerializer):
            raise InvalidSerializerError()

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return self._get_serializer_from_param()

    def _build_serializer_from_fields(self, fields):
        model_class = get_attr(self, 'queryset.model',
                               get_attr(self.serializer_class, 'Meta.model', None))
        exclude_fields = get_attr(self._default_serializer, 'Meta.exclude', [])

        # field_list = target
        field_list = list(filter(lambda s: s not in exclude_fields, fields))

        return serializer_factory(model_class,
                                  self.serializer_class,
                                  exclude=(),
                                  fields=field_list,
                                  )

    def _get_serializer_from_param(self, name=None):
        if name is None:
            name = self.request.query_params.get(self.serializer_field_param, 'std')

        if name == 'std':
            return self._default_serializer

        target = self.serializers_fieldsets.get(name, None)
        if isinstance(target, DynamicSerializer):
            field_list = target.get_fields(self)
            return self._build_serializer_from_fields(field_list)
        elif isinstance(target, (list, tuple)):
            return self._build_serializer_from_fields(target)
        elif isclass(target):  # Serializer class
            return target
        else:  # Standard Serializer
            raise InvalidSerializerError
