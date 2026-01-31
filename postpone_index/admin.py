"""
Admin interface
"""

from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from postpone_index.models import PostponedSQL


class PostponedSQLAdminMixin:
    list_display = ('d', 'description', 'table', 'db_index')
    list_display_links = ('d', 'description')
    search_fields = ('description', 'table', 'db_index')
    list_filter = (
        'table',
        'done'
    )

    def d(self, obj):
        return '✅' if obj.done else '🚫' if obj.error else '➡'
    d.short_description = _('Status')


if not getattr(settings, 'POSTPONE_INDEX_IGNORE', False) and not getattr(settings, 'POSTPONE_INDEX_ADMIN_IGNORE', False):
    @admin.register(PostponedSQL)
    class PostponedSQLAdmin(PostponedSQLAdminMixin, admin.ModelAdmin):
        pass
