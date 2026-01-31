"""Module Tests"""

from django.core.management import call_command
from django.test import override_settings

from postpone_index import testing_utils


class ModuleTest(testing_utils.TestCase):
    __doc__ = __doc__

    module_name = __name__.split('.')[0]

    def test_000_whole_migrate(self):
        """Test the whole module migration"""
        with override_settings(
            POSTPONE_INDEX_IGNORE=True
        ):
            call_command('migrate', self.module_name, 'zero')
        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            call_command('migrate', self.module_name)
            self.assertTrue(not self._check_postponed_sql_empty(), 'No Postponed SQL after migrations')
            call_command('apply_postponed', 'run', '-x')
            call_command('apply_postponed', 'cleanup')
            self._assert_postponed_sql_empty()

    def test_001_migrate_step_by_step(self):
        """Test migrations step by step"""
        with override_settings(
            POSTPONE_INDEX_IGNORE=True
        ):
            call_command('migrate', self.module_name, 'zero')
        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            call_command('migrate', self.module_name, '0001')
            self.assertTrue(self._check_postponed_sql_empty())

            call_command('migrate', self.module_name, '0001')
            self.assertTrue(self._check_postponed_sql_empty())

            call_command('migrate', self.module_name, '0002')
            self.assertTrue(self._check_postponed_sql_empty())

            call_command('migrate', self.module_name, '0003')
            self.assertTrue(not self._check_postponed_sql_empty())
            call_command('apply_postponed', 'run', '-x')
            call_command('apply_postponed', 'cleanup')
            self._assert_postponed_sql_empty()
