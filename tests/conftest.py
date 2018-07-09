import os
import sys
import pytest
import logging


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)
    logger = logging.getLogger("dynamic_serializer")
    handler = logging.NullHandler()
    # handler = logging.StreamHandler()
    logger.handlers = [handler]



@pytest.fixture
def demomodel():
    from demo.factories import DemoModelFactory
    return DemoModelFactory()
