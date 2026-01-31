"""Utility for special migration cases"""


class PostponeIndexIgnoreMigrationMixin:
    """Migration class mixin to avoid postpone index"""

    def apply(self, project_state, schema_editor, *av, **kw):
        """Override to avoid postpone index"""

        schema_editor._postpone_index_ignore = True
        ret = super().apply(project_state, schema_editor, *av, **kw)
        schema_editor._postpone_index_ignore = False
        return ret

    def unapply(self, project_state, schema_editor, *av, **kw):
        """Override to avoid postpone index"""
        schema_editor._postpone_index_ignore = True
        ret = super().unapply(project_state, schema_editor, *av, **kw)
        schema_editor._postpone_index_ignore = False
        return ret
