"""Module Tests"""

from config import base_tests


class ModuleTest(base_tests.TestCase):
    __doc__ = __doc__

    module_name = __name__.split('.')[0]
    migrations = ('0001', '0002', '0003')
