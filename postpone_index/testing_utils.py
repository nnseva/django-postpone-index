"""Testing Utilities"""

from django.conf import settings
from django.test import TransactionTestCase

from postpone_index.models import PostponedSQL


class TestCase(TransactionTestCase):
    """Base module testcase class"""

    @staticmethod
    def _check_postponed_sql_empty(alias='default'):
        try:
            first = PostponedSQL.objects.using(alias).all().first()
            if not first:
                # No record
                return True
        except Exception:
            # No table
            return True
        return False

    @classmethod
    def _assert_postponed_sql_empty(cls, message=None, alias='default'):
        cls.assertTrue(cls._check_postponed_sql_empty(alias=alias), message or 'Postponed SQL list not empty')

    @classmethod
    def setUpClass(cls):
        cls.assertTrue(settings.POSTPONE_INDEX_IGNORE, 'Tests should be started with POSTPONE_INDEX_IGNORE=True')

    @classmethod
    def tearDownClass(cls):
        if not cls._check_postponed_sql_empty(alias='default'):
            PostponedSQL.objects.using('default').all().delete()
        if not cls._check_postponed_sql_empty(alias='additional'):
            PostponedSQL.objects.using('additional').all().delete()
