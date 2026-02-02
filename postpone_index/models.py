import logging
import os
import time

from unlimited_char.fields import CharField

from django.db import models, connections
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
package_folder = os.path.dirname(os.path.abspath(__file__))


class PostponedSQLQuerySet(models.QuerySet):
    """
    QuerySet for PostponedSQL model.

    Redefined for admin view when table is absent.
    """

    def _create_base_tables(self):
        """
        Create base package table if absent
        """
        if self._is_present():
            logger.debug('[%s] The PostponedSQL storage already exists', self.db)
            return
        logger.info('[%s] The PostponedSQL storage is absent, creating', self.db)
        with open(os.path.join(package_folder, 'sql/start.sql')) as f:
            sql = f.read()
        cursor = connections[self.db].cursor()
        cursor.execute(sql)

    def count(self):
        """
        Count only if table is present
        """
        if not self._is_present():
            return 0
        return super().count()

    def _is_present(self):
        """
        Check if table is present
        """
        cursor = connections[self.db].cursor()
        cursor.execute(
            """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = '%s' limit 1
            """ % PostponedSQL._meta.db_table
        )
        return bool(cursor.fetchall())


class PostponedSQLManager(models.Manager):
    """
    Manager for PostponedSQL model.

    Redefined for admin view when table is absent.
    """

    def get_queryset(self):
        """
        Get custom QuerySet
        """
        qs = PostponedSQLQuerySet(self.model, using=self._db)
        if not qs._is_present():
            return qs.none()
        return qs


class PostponedSQL(models.Model):
    """Model to store postponed SQL commands"""

    ts = models.BigIntegerField(
        primary_key=True, editable=False,
        default=time.time_ns,
        verbose_name=_('Timestamp ns'),
        help_text=_('Timestamp in nanoseconds')
    )
    description = CharField(
        verbose_name=_('Description'),
        help_text=_('Free-form short description')
    )
    sql = models.TextField(
        verbose_name=_('SQL'),
        help_text=_('Original SQL generated on the migration stage'),
    )
    table = CharField(
        blank=True, null=True, db_index=True,
        verbose_name=_('Table'),
        help_text=_('Table name if applied to the table')
    )
    db_index = CharField(
        blank=True, null=True, db_index=True,
        verbose_name=_('Index'),
        help_text=_('Index name if applied to the index')
    )
    fields = CharField(
        blank=True, null=True,
        verbose_name=_('Fields'),
        help_text=_('Field names separated by comma if applied to the fields')
    )
    done = models.BooleanField(
        default=False,
        verbose_name=_('Done'),
        help_text=_('Has the command been applied')
    )
    error = models.TextField(
        blank=True, null=True,
        verbose_name=_('Error'),
        help_text=_('Last error reported when tried to apply')
    )

    objects = PostponedSQLManager()

    @property
    def d(self):
        """Status mark"""
        return '[X]' if self.done else '[E]' if self.error else '[ ]'

    class Meta:
        managed = False
        verbose_name = _('Postponed SQL')
        verbose_name_plural = _('Postponed SQLs')

    def __str__(self):
        return self.description
