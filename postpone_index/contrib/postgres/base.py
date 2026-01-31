from django.db.backends.postgresql.base import (
    DatabaseWrapper as _DatabaseWrapper,
)

from postpone_index.contrib.postgres.schema import DatabaseSchemaEditor


class DatabaseWrapper(_DatabaseWrapper):
    """Database wrapper"""

    SchemaEditorClass = DatabaseSchemaEditor
