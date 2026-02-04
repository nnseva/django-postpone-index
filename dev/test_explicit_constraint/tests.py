"""Module Tests"""

from config import base_tests

from django.core.management import call_command
from django.db import IntegrityError
from django.test import override_settings


class ModuleTest(base_tests.TestCase):
    __doc__ = __doc__

    module_name = __name__.split('.')[0]

    def test_004_migrate_with_bad_unique_data(self):
        """Test migrations step by step"""
        with override_settings(
            POSTPONE_INDEX_IGNORE=True
        ):
            call_command('migrate', self.module_name, 'zero')
        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            call_command('migrate', self.module_name, '0002')

            from test_explicit_constraint.models import ExplicitConstraint1

            # Duplicate field1/field2/field3 - ok without apply_postponed
            ExplicitConstraint1.objects.create(field1='qwerty', field2='uiop', field3='asdfg')
            duplicate = ExplicitConstraint1.objects.create(field1='qwerty', field2='uiop', field3='asdfg')

            with self.assertRaises(IntegrityError):
                # Generates error on duplicate records
                call_command('apply_postponed', 'run', '-x')
            duplicate.delete()  # remove duplicate

            call_command('apply_postponed', 'run', '-x')  # Now it should be OK
            call_command('apply_postponed', 'cleanup')
            self._assert_postponed_sql_empty()

            call_command('migrate', self.module_name, '0003')

            # Duplicate field1/field2/field3 - ok
            # after the migration deleted old unique and not yet created a new one
            duplicate = ExplicitConstraint1.objects.create(field1='qwerty', field2='uiop', field3='asdfg')

            with self.assertRaises(IntegrityError):
                # Generates error on duplicate records
                call_command('apply_postponed', 'run', '-x')
            duplicate.delete()  # remove duplicate

            call_command('apply_postponed', 'run', '-x')  # Now it should be OK
            call_command('apply_postponed', 'cleanup')
            self._assert_postponed_sql_empty()
