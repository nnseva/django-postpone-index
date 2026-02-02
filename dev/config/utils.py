"""Utilities for the development config"""

import os
import unittest
import unittest.loader

from django.apps import apps
from django.test.runner import DiscoverRunner


class DjangoTestLoader(unittest.loader.TestLoader):
    """Searches tests only in application directories"""
    def discover(self, start_dir, pattern='test*.py', *av, **kw):
        self._django_start_dir = os.path.abspath(start_dir)
        return super().discover(start_dir, pattern=pattern, *av, **kw)

    def _find_tests(self, start_dir, pattern, *av, **kw):
        # Recurse catch
        if start_dir == self._django_start_dir:
            for config in apps.get_app_configs():
                if os.path.abspath(config.path).startswith(os.path.abspath(start_dir)):
                    yield from super()._find_tests(config.path, pattern, *av, **kw)
        else:
            yield from super()._find_tests(start_dir, pattern, *av, **kw)


class DjangoDiscoverRunner(DiscoverRunner):
    test_loader = DjangoTestLoader()
