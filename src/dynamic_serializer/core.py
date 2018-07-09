# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
from inspect import isclass

from django.utils.functional import cached_property
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


class ParserStrategy(object):
    param_name = 'serializer'

    def __init__(self, viewset):
        self.viewset = viewset


class SerializerStrategy(ParserStrategy):
    param_name = 'serializer'

    # serializers_fieldsets = {'std': None}

    @cached_property
    def _default_serializer(self):
        return self.viewset.serializers_fieldsets.get('std',
                                                      self.viewset.serializer_class) or self.viewset.serializer_class

    def _get_serializer_from_param(self):
        model_class = get_attr(self.viewset, 'queryset.model',
                               get_attr(self.viewset.serializer_class, 'Meta.model', None))
        exclude_fields = get_attr(self._default_serializer, 'Meta.exclude', [])

        name = self.viewset.request.query_params.get(self.param_name, 'std')
        field_list_or_serializer = self.viewset.serializers_fieldsets.get(name, None)
        if isinstance(field_list_or_serializer, (list, tuple)):  # fields list
            field_list = field_list_or_serializer
        elif isclass(field_list_or_serializer):  # Serializer class
            return field_list_or_serializer
        else:  # Standard Serializer
            return self._default_serializer

        filter(lambda s: s not in exclude_fields, field_list)

        return serializer_factory(model_class,
                                  self.viewset.serializer_class,
                                  exclude=(),
                                  fields=field_list,
                                  )


class FieldsStrategy(ParserStrategy):
    param_name = '_fields'

    def _get_serializer_from_param(self):
        model_class = get_attr(self.viewset, 'queryset.model',
                               get_attr(self.viewset.serializer_class, 'Meta.model', None))
        requested_fields = list(filter(lambda s: bool(s), map(lambda s: s.strip(),
                                                              self.viewset.request.query_params.get(self.param_name,
                                                                                                    "").split(
                                                                  ","))))
        if not requested_fields:
            return self.viewset.serializer_class

        field_list = filter(lambda s: s in self.viewset.base_fields, requested_fields)
        return serializer_factory(model_class,
                                  self.viewset.serializer_class,
                                  exclude=(),
                                  fields=list(field_list, )
                                  )


class DynamicMixin(object):
    _serializers_classes = {}
    strategy_class = None
    serializers_fieldsets = {'std': None}

    def __init__(self, *args, **kwargs):
        super(DynamicMixin, self).__init__()
        self.strategy = self.strategy_class(self)

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
        return self.strategy._get_serializer_from_param()


class DynamicSerializerMixin(DynamicMixin):
    param_name = 'serializer'
    serializers_fieldsets = {'std': None}
    strategy_class = SerializerStrategy


class DynamicFieldsSerializerMixin(DynamicMixin):
    param_name = '_fields'
    strategy_class = FieldsStrategy

    @property
    def base_fields(self):
        return get_attr(self._default_serializer(), 'fields', []).keys()


class DynamicOutput(DynamicFieldsSerializerMixin):
    strategy_classes = [FieldsStrategy, SerializerStrategy]

    def __init__(self, *args, **kwargs):
        super(DynamicOutput, self).__init__()
        self.strategies = [h(self) for h in self.strategy_classes]

    def get_serializer_class(self):
        for handler in self.strategies:
            if handler.param_name in self.request.query_params:
                return handler._get_serializer_from_param()
        return self.serializer_class
