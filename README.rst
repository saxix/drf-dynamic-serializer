======================
DRF Dynamic Serializer
======================

.. image:: https://badge.fury.io/py/drf-dynamic-serializer.png
    :target: https://badge.fury.io/py/drf-dynamic-serializer


.. image:: https://badge.fury.io/py/drf-dynamic-serializer.png
    :target: http://badge.fury.io/py/drf-dynamic-serializer

.. image:: https://travis-ci.org/saxix/drf-dynamic-serializer.png?branch=master
        :target: https://travis-ci.org/saxix/drf-dynamic-serializer


Simple plugin for DRF to customise output

Example
~~~~~~~

Consider this starting code


    class UserSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = User
            exclude = ('date_joined', 'password')


    class BaseViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer

Now add some salt


    class UserSerializerShort(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name')


    class DynamicSerializerViewSet(DynamicSerializerMixin, BaseViewSet):
        serializers_fieldsets = {'light': ('last_name', 'first_name'),
                                 'short': UserSerializerShort}

this allows queries like:

    - /users/?
    - /users/?serializer=std
    - /users/?serializer=light
    - /users/?serializer=short


... and now a bit of pepper


    class DynamicFieldsSerializerViewSet(DynamicFieldsSerializerMixin, BaseViewSet):
        pass

this allows queries like:

    - /users/?
    - /users/?_fields=email,first_name,is_active


... finally full seasoning


    class DynamicOutputViewSet(DynamicFieldsSerializerMixin, BaseViewSet):
        pass



Links
~~~~~

+--------------------+----------------+--------------+----------------------------+
| Stable             | |master-build| | |master-cov| |                            |
+--------------------+----------------+--------------+----------------------------+
| Development        | |dev-build|    | |dev-cov|    |                            |
+--------------------+----------------+--------------+----------------------------+
| Project home page: |https://github.com/saxix/drf-dynamic-serializer             |
+--------------------+---------------+--------------------------------------------+
| Issue tracker:     |https://github.com/saxix/drf-dynamic-serializer/issues?sort |
+--------------------+---------------+--------------------------------------------+
| Download:          |http://pypi.python.org/pypi/drf-dynamic-serializer/         |
+--------------------+---------------+--------------------------------------------+
| Documentation:     |https://drf-dynamic-serializer.readthedocs.org/en/latest/   |
+--------------------+---------------+--------------+-----------------------------+

.. |master-build| image:: https://secure.travis-ci.org/saxix/drf-dynamic-serializer.png?branch=master
                    :target: http://travis-ci.org/saxix/drf-dynamic-serializer/

.. |master-cov| image:: https://codecov.io/gh/saxix/drf-dynamic-serializer/branch/master/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/drf-dynamic-serializer

.. |dev-build| image:: https://secure.travis-ci.org/saxix/drf-dynamic-serializer.png?branch=develop
                  :target: http://travis-ci.org/saxix/drf-dynamic-serializer/

.. |dev-cov| image:: https://codecov.io/gh/saxix/drf-dynamic-serializer/branch/develop/graph/badge.svg
                    :target: https://codecov.io/gh/saxix/drf-dynamic-serializer



