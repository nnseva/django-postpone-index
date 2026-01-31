import time

from unlimited_char.fields import CharField

from django.db import models
from django.utils.translation import gettext_lazy as _


class PostponedSQL(models.Model):
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
