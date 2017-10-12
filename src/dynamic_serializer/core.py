# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from inspect import isclass

from django.utils.functional import cached_property
from rest_framework.serializers import ModelSerializer, BaseSerializer

logger = logging.getLogger(__name__)

cache = {}


def serializer_factory(model, base=ModelSerializer, fields=None, exclude=None):
    """
    >>> from django.contrib.auth.models import User
    >>> s = serializer_factory(User)
    """
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude

    parent = (object,)
    if hasattr(base, 'Meta'):
        parent = (base.Meta, object)
    Meta = type(str('Meta'), parent, attrs)
    class_name = model.__name__ + 'Serializer'
    return type(base)(class_name.encode('utf8'), (base,), {'Meta': Meta, })


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


class DynamicSerializerMixin(object):
    """
    ViewSet Mixin that allow to limit the fields returned
    by the serializer.

    Es.
        class MyViewSet(DynamicSerializerViewSetMixin, BaseModelViewSet):
            model = User
            serializer_class = UserSerializer
            serializers_fieldsets = {'std': None,
                                      'brief' : ('username', 'email')
                                      }
    this allow calls like

        /api/v1/user/?serializer=brief

    """
    serializers_fieldsets = {'std': None}
    _serializers_classes = {}
    serializer_class = None
    header_only_serializers = ['andy', ]  # cannot use these in GET, only accept these in headers

    @cached_property
    def _default_serializer(self):
        return self.serializers_fieldsets.get('std',
                                              self.serializer_class) or self.serializer_class

    def get_requested_serializer(self, request):
        name = request.query_params.get('serializer', 'std')

        return self.serializers_fieldsets.get(name, None)

    def get_serializer_class(self):

        model_class = get_attr(self, 'queryset.model',
                               get_attr(self.serializer_class, 'Meta.model', None))
        exclude_fields = get_attr(self._default_serializer, 'Meta.exclude', [])

        field_list_or_serializer = self.get_requested_serializer(self.request)

        if isinstance(field_list_or_serializer, (list, tuple)):  # fields list
            field_list = field_list_or_serializer
        elif isclass(field_list_or_serializer):  # Serializer class
            return field_list_or_serializer
        else:  # Standard Serializer
            return self.serializer_class

        filter(lambda s: s not in exclude_fields, field_list)

        return serializer_factory(model_class,
                                  self.serializer_class,
                                  exclude=(),
                                  fields=field_list,
                                  )

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
        # serializer_class = kwargs.pop('serializer_class', None)
        # if serializer_class is None:
        serializer_class = self.get_serializer_class()
        if not issubclass(serializer_class, BaseSerializer):
            raise InvalidSerializerError()

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
