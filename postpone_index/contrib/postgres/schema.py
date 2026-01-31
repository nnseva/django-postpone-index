"""Schema editor with concurrent index creation support."""
import logging
import os
import os.path

from django.conf import settings
from django.db.backends.postgresql.schema import (
    DatabaseSchemaEditor as _DatabaseSchemaEditor,
)

from postpone_index.utils import Utils


logger = logging.getLogger(__name__)
package_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class DatabaseSchemaEditorMixin(Utils):
    """Mixin to embed into DatabaseSchemaEditor"""
    _base_tables_created = False

    def _create_base_tables(self):
        """
        Create base package tables on the first access to this function
        """
        if self._base_tables_created:
            return

        # Avoid circular import
        from postpone_index.models import PostponedSQL

        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '%s' limit 1" % PostponedSQL._meta.db_table)
        if cursor.fetchall():
            self._base_tables_created = True
            logger.debug('[%s] The PostponedSQL storage already exists', self.connection.alias)
            return
        logger.info('[%s] The PostponedSQL storage is absent, creating', self.connection.alias)
        with open(os.path.join(package_folder, 'sql/start.sql')) as f:
            sql = f.read()
        cursor.execute(sql)
        self._base_tables_created = True

    def _ignore(self):
        """Check whether to ignore the extension"""
        return getattr(settings, 'POSTPONE_INDEX_IGNORE', False) or getattr(self, '_postpone_index_ignore', False)

    def execute(self, sql, params=()):
        """
        Overriden for execute processing with special handling for index operations.

        All indexing operations are postponed by writing to a special table instead of execution.

        They will be executed later in CONCURRENTLY manner.
        """
        if self._ignore():
            return super().execute(sql, params)

        self._create_base_tables()

        # Avoid circular import
        from postpone_index.models import PostponedSQL

        if match := self._create_index_re.fullmatch(str(sql)):
            # Postpone index creation
            index_name = match.group('index_nameq') or match.group('index_name')
            table_name = match.group('table_nameq') or match.group('table_name')
            columns = ','.join(self._extract_column_names(match.group('rest')))
            description = 'Create Index "%s" on "%s" (%s)' % (
                index_name,
                table_name,
                columns
            )
            PostponedSQL.objects.using(self.connection.alias).create(
                sql=str(sql),
                description=description,
                table=table_name,
                db_index=index_name,
                fields=columns
            )
            logger.info('[%s] Postponed %s', self.connection.alias, description)
        elif match := self._add_constraint_re.fullmatch(str(sql)):
            # Postpone constraint creation
            index_name = match.group('index_nameq') or match.group('index_name')
            table_name = match.group('table_nameq') or match.group('table_name')
            columns = ','.join(self._extract_column_names(match.group('rest')))
            description = 'Add Unique Constraint "%s" on "%s" (%s)' % (
                index_name,
                table_name,
                columns,
            )
            PostponedSQL.objects.using(self.connection.alias).create(
                sql=str(sql),
                description=description,
                table=table_name,
                db_index=index_name,
                fields=columns
            )
            logger.info('[%s] Postponed %s', self.connection.alias, description)
        else:
            if match := self._drop_index_re.fullmatch(str(sql)):
                # Override to ignore inexistent index drop error
                index_name = match.group('index_nameq') or match.group('index_name')
                if PostponedSQL.objects.using(self.connection.alias).filter(db_index=index_name, done=False).delete()[0]:
                    logger.info('[%s] Removed Index %s from postponed', self.connection.alias, index_name)
                # Avoid errors on introspecting inexistent index
                try:
                    return super().execute(sql, params)
                    logger.info('[%s] Drop index %s success', self.connection.alias, index_name)
                except Exception as ex:
                    logger.info('[%s] Drop index %s ignored: %s', self.connection.alias, index_name, ex)
            elif match := self._drop_constraint_re.fullmatch(str(sql)):
                # Override to ignore inexistent constraint drop error
                index_name = match.group('index_nameq') or match.group('index_name')
                table_name = match.group('table_nameq') or match.group('table_name')
                if PostponedSQL.objects.using(self.connection.alias).filter(db_index=index_name, table=table_name, done=False).delete()[0]:
                    logger.info('[%s] Removed Constraint %s on %s from postponed', self.connection.alias, index_name, table_name)
                # Avoid errors on introspecting inexistent constraint
                try:
                    return super().execute(sql, params)
                    logger.info('[%s] Drop constraint %s success', self.connection.alias, index_name)
                except Exception as ex:
                    logger.info('[%s] Drop constraint %s ignored: %s', self.connection.alias, index_name, ex)
            elif match := self._drop_table_re.fullmatch(str(sql)):
                # Table dropped cancels all postponed operations related
                table_name = match.group('table_nameq') or match.group('table_name')
                if PostponedSQL.objects.using(self.connection.alias).filter(table=table_name, done=False).delete()[0]:
                    logger.info('[%s] Removed all indexes on table %s from postponed', self.connection.alias, table_name)
                return super().execute(sql, params)
            elif match := self._drop_column_re.fullmatch(str(sql)):
                # Table dropped cancels all postponed operations related
                table_name = match.group('table_nameq') or match.group('table_name')
                column_name = match.group('column_nameq') or match.group('column_name')
                if PostponedSQL.objects.using(self.connection.alias).filter(
                    table=table_name, fields__contains='"%s"' % column_name, done=False
                ).delete()[0]:
                    logger.info(
                        '[%s] Removed all indexes on column %s of table %s from postponed',
                        self.connection.alias, column_name, table_name
                    )
                return super().execute(sql, params)
            else:
                logger.debug('[%s] No special statements: %s', self.connection.alias, sql)
                return super().execute(sql, params)

    def _alter_field(
        self, model, old_field, new_field, old_type, new_type,
        old_db_params, new_db_params, *args, **kw
    ):
        """Overriden for special field attributes processing"""

        # The original code uses database introspection to decide whether the
        # index to be removed is present. We override the function before the introspection calls
        # to remove the postponed index creation jobs instead.

        if self._ignore():
            return super()._alter_field(
                model, old_field, new_field, old_type, new_type,
                old_db_params, new_db_params, *args, **kw
            )

        self._create_base_tables()

        # Avoid circular import
        from postpone_index.models import PostponedSQL

        suffixes = []

        if old_field.unique and not new_field.unique:
            # Delete unique field attribute cancels all postponed operations related
            suffixes.append('_uniq')

        if old_field.db_index and not new_field.db_index:
            # Delete db_index field attribute cancels all postponed operations related
            suffixes.append('')
            suffixes.append('_like')

        if old_db_params['check'] != new_db_params['check'] and old_db_params['check']:
            # Delete check field attribute cancels all postponed operations related
            suffixes.append('_check')

        for suffix in suffixes:
            index_name = self._create_index_name(
                model._meta.db_table,
                [old_field.column],
                suffix
            )
            if PostponedSQL.objects.using(self.connection.alias).filter(table=model._meta.db_table, db_index=index_name, done=False).delete()[0]:
                logger.info('[%s] Removed single index %s on %s from postponed', self.connection.alias, index_name, model._meta.db_table)

        return super()._alter_field(
            model, old_field, new_field, old_type, new_type,
            old_db_params, new_db_params, *args, **kw
        )

    def _delete_composed_index(self, model, fields, constraint_kwargs, sql):
        """Overriden for special composed index processing"""

        # The original code uses database introspection to decide whether the
        # index to be removed is present. We override the function before the introspection calls
        # to remove the postponed index creation jobs instead.

        if self._ignore():
            return super()._delete_composed_index(model, fields, constraint_kwargs, sql)

        self._create_base_tables()

        # Avoid circular import
        from postpone_index.models import PostponedSQL

        # Delete composed index cancels all postponed operations related
        index_name = self._create_index_name(
            model._meta.db_table,
            [model._meta.get_field(f).column for f in fields],
            '_uniq' if (constraint_kwargs or {}).get('unique', False) else '_idx'
        )

        if PostponedSQL.objects.using(self.connection.alias).filter(table=model._meta.db_table, db_index=index_name, done=False).delete()[0]:
            logger.info('[%s] Removed composed index %s on %s from postponed', self.connection.alias, index_name, model._meta.db_table)

        # Avoid errors on introspecting inexistent compound index
        try:
            super()._delete_composed_index(model, fields, constraint_kwargs, sql)
            logger.info('[%s] Delete composed %s on %s success', self.connection.alias, index_name, model._meta.db_table)
        except Exception as ex:
            logger.info('[%s] Delete composed %s on %s ignored: %s', self.connection.alias, index_name, model._meta.db_table, ex)


class DatabaseSchemaEditor(DatabaseSchemaEditorMixin, _DatabaseSchemaEditor):
    pass
