"""Some utilities"""

import re
from collections.abc import MappingView


class ObjMap(MappingView):
    """Gives access to any attribute using map protocol, combining with another map for defaults"""

    def __init__(self, obj, defaults=None):
        """Initialize by the original object"""
        self._obj = obj
        self._defaults = defaults or {}

    def __getitem__(self, k):
        """Override to get access"""
        try:
            return getattr(self._obj, k)
        except AttributeError:
            return self._defaults[k]


class Utils:
    """Utilities class"""
    _create_index_re = re.compile(
        r'^\s*CREATE\s+(?P<unique>UNIQUE\s+)?INDEX\s+(IF\s+NOT\s+EXISTS\s+)?'
        r'(((?P<iq>")?(?P<index_nameq>[^"]+)(?P=iq))|(?P<index_name>[^\s]+))'
        r'\s+ON\s+(?P<only>ONLY\s+)?'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _drop_index_re = re.compile(
        r'^\s*DROP\s+INDEX\s+(IF\s+EXISTS\s+)?'
        r'(((?P<iq>")?(?P<index_nameq>[^"]+)(?P=iq))|(?P<index_name>[^\s]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _drop_table_re = re.compile(
        r'^\s*DROP\s+TABLE\s+(IF\s+EXISTS\s+)?'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _add_constraint_re = re.compile(
        r'^\s*ALTER\s+TABLE\s+'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'\s+ADD\s+CONSTRAINT\s+'
        r'(((?P<iq>")?(?P<index_nameq>[^"]+)(?P=iq))|(?P<index_name>[^\s]+))'
        r'\s+UNIQUE\s+'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _drop_constraint_re = re.compile(
        r'^\s*ALTER\s+TABLE\s+'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'\s+DROP\s+CONSTRAINT\s+'
        r'(((?P<iq>")?(?P<index_nameq>[^"]+)(?P=iq))|(?P<index_name>[^\s]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _drop_column_re = re.compile(
        r'^\s*ALTER\s+TABLE\s+'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'\s+DROP\s+COLUMN\s+'
        r'(((?P<cq>")?(?P<column_nameq>[^"]+)(?P=cq))|(?P<column_name>[^\s]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _rename_column_re = re.compile(
        r'^\s*ALTER\s+TABLE\s+'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'\s+RENAME\s+COLUMN\s+'
        r'(((?P<cq>")?(?P<column_nameq>[^"]+)(?P=cq))|(?P<column_name>[^\s]+))'
        r'\s+TO\s+'
        r'(((?P<nq>")?(?P<ncolumn_nameq>[^"]+)(?P=nq))|(?P<ncolumn_name>[^\s]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _rename_table_re = re.compile(
        r'^\s*ALTER\s+TABLE\s+'
        r'(("?)public("?)\.)?(((?P<tq>")?(?P<table_nameq>[^"]+)(?P=tq))|(?P<table_name>[_a-zA-Z0-9]+))'
        r'\s+RENAME\s+TO\s+'
        r'(((?P<nq>")?(?P<ntable_nameq>[^"]+)(?P=nq))|(?P<ntable_name>[^\s]+))'
        r'(?P<rest>.*)$',
        re.IGNORECASE | re.MULTILINE
    )
    _column_name_re = re.compile(
        r'(((?P<cq>")(?P<column_nameq>[^"]+)(?P=cq))|(?P<column_name>[^\s]+))',
        re.IGNORECASE | re.MULTILINE
    )
    _enclosed_re = re.compile(
        r'\((?P<enclosed>[^\(\)]*)\)',
        re.IGNORECASE | re.MULTILINE
    )

    @classmethod
    def _extract_column_names(cls, rest):
        """Extracts column names from complex index suffix"""
        rest = cls._extract_enclosed(rest)
        while match := cls._enclosed_re.search(rest):
            rest = rest[:match.start()] + rest[match.end():]
        ret = []
        for column in [c for c in rest.split(',') if c.strip()]:
            match = cls._column_name_re.search(column)
            if not match:
                continue
            ret.append('"%s"' % (match.group('column_nameq') or match.group('column_name')))
        return ret

    @classmethod
    def _extract_enclosed(cls, rest):
        """Extract first enclosed statement with recursive parentheses"""
        deep = 0
        start = 0
        end = 0
        for i, c in enumerate(rest):
            if c == '(':
                if deep == 0:
                    start = i + 1
                deep += 1
            elif c == ')':
                deep -= 1
                if deep == 0:
                    end = i
                    break
        if end == 0:
            return rest
        return rest[start:end]
