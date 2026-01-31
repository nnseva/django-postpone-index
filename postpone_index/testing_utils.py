"""Testing Utilities"""

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from postpone_index.models import PostponedSQL


class TestCase(TransactionTestCase):
    """Base module testcase class"""

    @staticmethod
    def _check_postponed_sql_empty():
        try:
            first = PostponedSQL.objects.all().first()
            if not first:
                # No record
                return True
        except Exception:
            # No table
            return True
        return False

    @classmethod
    def _assert_postponed_sql_empty(cls, message=None):
        cls.assertTrue(cls._check_postponed_sql_empty(), message or 'Postponed SQL list not empty')

    @classmethod
    def setUpClass(cls):
        cls.assertTrue(settings.POSTPONE_INDEX_IGNORE, 'Tests should be started with POSTPONE_INDEX_IGNORE=True')

    @classmethod
    def tearDownClass(cls):
        if not cls._check_postponed_sql_empty():
            PostponedSQL.objects.all().delete()
