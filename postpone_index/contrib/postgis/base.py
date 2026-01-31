from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as _DatabaseWrapper,
)

from postpone_index.contrib.postgres.schema import DatabaseSchemaEditor

class DatabaseWrapper(_DatabaseWrapper):
    """Database wrapper"""

    SchemaEditorClass = DatabaseSchemaEditor
