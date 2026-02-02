"""Schema editor with concurrent index creation support."""

from django.contrib.gis.db.backends.postgis.schema import (
    PostGISSchemaEditor as _DatabaseSchemaEditor,
)

from postpone_index.contrib.postgres.schema import DatabaseSchemaEditorMixin


class DatabaseSchemaEditor(DatabaseSchemaEditorMixin, _DatabaseSchemaEditor):
    pass
