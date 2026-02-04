"""Base module test with base migration tests"""

from django.apps import apps
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.db.migrations.loader import MigrationLoader
from django.test import override_settings

from postpone_index import testing_utils


def _list_migrations(app_name):
    """Lists all module migrations"""

    loader = MigrationLoader(connection, ignore_no_migrations=True)
    graph = loader.graph
    ret = []
    for node in graph.leaf_nodes(app_name):
        for plan_node in graph.forwards_plan(node):
            if plan_node[0] == app_name:
                ret.append(plan_node[1])
    return ret


class TestCase(testing_utils.TestCase):
    __doc__ = __doc__

    maxDiff = None

    module_name = None  # Replace in child to the name of the module to test

    @property
    def migrations(self):
        """All module migrations"""
        return _list_migrations(self.module_name)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_000_whole_migrate(self):
        """Test the whole module migration"""
        with override_settings(
            POSTPONE_INDEX_IGNORE=True
        ):
            call_command('migrate', self.module_name, 'zero')
            call_command('migrate', self.module_name, 'zero', '--database=additional')
        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            call_command('migrate', self.module_name)
            call_command('migrate', self.module_name, '--database=additional')
            self.assertTrue(not self._check_postponed_sql_empty(alias='default'), 'No Postponed SQL after migrations')
            self.assertTrue(not self._check_postponed_sql_empty(alias='additional'), 'No Postponed SQL after migrations')
            call_command('apply_postponed', 'run', '-x')
            call_command('apply_postponed', 'run', '-x', '--database=additional')
            call_command('apply_postponed', 'cleanup')
            call_command('apply_postponed', 'cleanup', '--database=additional')
            self._assert_postponed_sql_empty(alias='default')
            self._assert_postponed_sql_empty(alias='additional')

    def test_001_migrate_step_by_step(self):
        """Test migrations step by step"""
        with override_settings(
            POSTPONE_INDEX_IGNORE=True
        ):
            call_command('migrate', self.module_name, 'zero')
        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            for migration_id in self.migrations:
                call_command('migrate', self.module_name, migration_id)
                call_command('apply_postponed', 'run', '-x')
                call_command('apply_postponed', 'cleanup')
                self._assert_postponed_sql_empty()

            migrations_reversed = list(reversed(self.migrations[:-1])) + ['zero']

            for migration_id in migrations_reversed:
                call_command('migrate', self.module_name, migration_id)
                call_command('apply_postponed', 'run', '-x')
                call_command('apply_postponed', 'cleanup')
                self._assert_postponed_sql_empty()

    def test_002_migrate_equaliry(self):
        """Test and compare migrations with and without postpone index using introspection"""

        # Baseline: default settings (tests run with POSTPONE_INDEX_IGNORE=True).
        call_command('migrate', self.module_name, 'zero')

        migration_before = 'zero'

        for migration_id in self.migrations:
            # Store introspection
            call_command('migrate', self.module_name, migration_id)
            baseline = self.introspect_app_schema(self.module_name)
            call_command('migrate', self.module_name, migration_before)

            # With postpone_index enabled.
            with override_settings(POSTPONE_INDEX_IGNORE=False):
                call_command('migrate', self.module_name, migration_id)
                call_command('apply_postponed', 'run', '-x')
                call_command('apply_postponed', 'cleanup')
                self._assert_postponed_sql_empty()
                postponed = self.introspect_app_schema(self.module_name)

            self.assertEqual(
                baseline,
                postponed,
                'Introspection mismatch for migration %s' % (
                    migration_id,
                ),
            )
            migration_before = migration_id

    @staticmethod
    def _field_info_to_dict(field_info):
        return {
            'name': field_info.name,
            'type_code': field_info.type_code,
            'display_size': getattr(field_info, 'display_size', None),
            'internal_size': getattr(field_info, 'internal_size', None),
            'precision': getattr(field_info, 'precision', None),
            'scale': getattr(field_info, 'scale', None),
            'null_ok': getattr(field_info, 'null_ok', None),
        }

    @staticmethod
    def _normalize_constraint_info(info):
        foreign_key = info.get('foreign_key')
        if foreign_key is not None:
            foreign_key = tuple(foreign_key)
        return {
            'columns': tuple(info.get('columns') or ()),
            'primary_key': bool(info.get('primary_key')),
            'unique': bool(info.get('unique')),
            'foreign_key': foreign_key,
            'check': bool(info.get('check')),
            'index': bool(info.get('index')),
            'orders': tuple(info.get('orders') or ()),
            'type': info.get('type'),
        }

    @classmethod
    def _normalize_indexes(cls, constraints):
        """Extract a stable index-only snapshot from get_constraints().

        Django introspection exposes indexes via get_constraints() with info['index']=True.
        We expose them separately to make intent explicit in tests.
        """

        indexes = []
        for name, info in constraints.items():
            normalized = cls._normalize_constraint_info(info)
            if not normalized['index']:
                continue
            indexes.append({
                'name': name,
                'columns': normalized['columns'],
                'unique': normalized['unique'],
                'orders': normalized['orders'],
                'type': normalized['type'],
                'primary_key': normalized['primary_key'],
            })

        indexes.sort(key=lambda x: x['name'])
        return indexes

    @classmethod
    def introspect_app_schema(cls, app_label, using=DEFAULT_DB_ALIAS):
        """Introspect app tables (columns, constraints, indexes).

        Result is a JSON-serializable structure suitable for equality comparisons.
        """

        connection = connections[using]
        app_config = apps.get_app_config(app_label)
        model_tables = sorted({m._meta.db_table for m in app_config.get_models()})

        with connection.cursor() as cursor:
            existing_tables = set(connection.introspection.table_names(cursor))
            snapshot = {}
            for table_name in model_tables:
                if table_name not in existing_tables:
                    continue

                description = connection.introspection.get_table_description(cursor, table_name)
                columns = [cls._field_info_to_dict(c) for c in description]

                constraints = connection.introspection.get_constraints(cursor, table_name)
                normalized_constraints = {
                    name: cls._normalize_constraint_info(info)
                    for name, info in constraints.items()
                }

                snapshot[table_name] = {
                    'columns': columns,
                    'constraints': normalized_constraints,
                    'indexes': cls._normalize_indexes(constraints),
                }

            return snapshot
