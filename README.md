[![Tests](https://github.com/nnseva/django-postpone-index/actions/workflows/ci.yml/badge.svg)](https://github.com/nnseva/django-postpone-index/actions/workflows/ci.yml)

# Django Postpone Index

This package provides modules and tools to postpone any index creation instead doing it inside the migration,
to provide *Zero Downtime Migration* feature.

The package is now using the PostgresSQL-specific `CREATE INDEX CONCURRENTLY` SQL command, so is applicable
only to the PostgreSQL backend.

## Installation

*Stable version* from the PyPi package repository
```bash
pip install django-postpone-index
```

*Last development version* from the GitHub source version control system
```
pip install git+git://github.com/nnseva/django-postpone-index.git
```

## Problem Description

Large data leads to long index creation time.

When the migration is automatically created, it executes all SQL commands creating index inside a transaction.

Large data and index creation inside a transaction lead to long-term table lock which blocks any data writting to the table.

On the other side, `CREATE INDEX CONCURRENTLY` SQL command may solve the problem, but this SQL command can not be executed inside a transaction block.

The `AddIndexConcurrently` might be created in a separate migration, moving out the automatically generated `AddIndex` from the migration,
but not all indexes are created using `AddIndex`.

## Solution

All index creation SQL commands (as well as unique constraints creation) are catched
and postponed using a special `PostponedSQL` model (the `DROP INDEX` and `DROP CONSTRAINT` SQL commands
are still executed immediately).

When the migration is finished, the postponed indexes may be created in a separate process
using `CREATE INDEX CONCURRENTLY` SQL command by the `apply_postponed` management command.
Apart from the standard migration, this process doesn't lock the whole table for a long time.

Failed index creation statements don't lead to the command failure
(until a special command line parameter passed). Every failed statement is stored
as erroneous instead. When the data is fixed, you can execute the `apply_postponed` management
command again to restore the failed indexes.

## Complex Use Cases

The following complex use cases are processed by the package.

- Several create/drop pairs. There can be several create/drop index pairs if several migrations applied at once.
- Back Migration. The both, forward and backward migrations are processed.
- Implicit index drop while removing the table. The Django doesn't issue a separate SQL to drop indexes of the dropped table.
- Implicit index drop while removing the field. The Django doesn't issue a separate SQL to drop indexes related to the dropped column.

## Using

Include the `postpone_index` application in `setting.py`:

```python
INSTALLED_APPS = [
    ...
    'postpone_index',
    ...
]
```

Use `pospone_index.contrib.postgres` or `postpone_index.contrib.postgis` engines instead of the Django-provided in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'postpone_index.contrib.postgres',
        ...
    }
}
```

If you provide your own database engine instead of the Django-provided, you can also
combine `pospone_index.contrib.postgres.schema.DatabaseSchemaEditorMixin` with your own Database Schema Editor, f.e.:

`mybackend/schema.py`
```python
from django.db.backends.postgresql.schema import DatabaseSchemaEditor as _DatabaseSchemaEditor
from pospone_index.contrib.postgres.schema import DatabaseSchemaEditorMixin

class PostponeIndexDatabaseSchemaEditor(DatabaseSchemaEditorMixin, _DatabaseSchemaEditor):
    # Your own code
    ...
```

`mybackend/base.py`
```python
from django.db.backends.postgresql.base import (
    DatabaseWrapper as _DatabaseWrapper,
)

from mybackend.schema import PostponeIndexDatabaseSchemaEditor


class DatabaseWrapper(_DatabaseWrapper):
    """Database wrapper"""

    SchemaEditorClass = PostponeIndexDatabaseSchemaEditor
    # Your own code
    ...
```

Execute `apply_postponed` management command every time after the `migrate` management command to create new postponed indexes.

Monitor `PostponedSQL` model instances to see errors on the SQL execution.

After the data is fixed, you can try to recreate the postponed invalid indexes just
calling the `apply_postponed` migration command again. All not-applied indexes will be tried to create again.

**NOTICE** the `apply_postponed` management command doesn't have any explicit locking mechanics. Avoid starting this
command concurrently with itself or another `migrate` command on the same database.

## Django testing

Django migrates testing database before tests. Always use `POSTPONE_INDEX_IGNORE = True` settings to avoid postpone index
for the testing database.

If you want to check your own migration with the postpone index switched on,
use the `postpone_index.testing_utils.TestCase` and `override_settings` Django feature with the following trick:

```python
from django.core.management import call_command
from django.test import override_settings
from postpone_index.models import PostponedSQL
from postpone_index import testing_utils

class ModuleTest(testing_utils.TestCase):
    # Notice that the base TestCase is TransactionalTestCase

    @classmethod
    def setUpClass(cls):
        # If you want to have customized setUpClass, call the method of the base class
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # If you want to have customized tearDownClass, call the method of the base class
        super().tearDownClass()

    def test_my_special_migration_case(self):
        """Explicitly check my migration with postpone_index"""

        module_to_check = "my_module"           # Your Django App
        migration_before_the_check = "0005"     # Just before your migration
        migration_to_check = "0006"             # The migration you check

        # Notice that POSTPONED_INDEX_IGNORE is True by default while testing
        call_command('migrate', module_to_check, migration_before_the_check)

        with override_settings(
            POSTPONE_INDEX_IGNORE=False
        ):
            # Here we can check how it's going with `postpone_index` activated

            # Check whether your migration works as expected with postponed indexes
            call_command('migrate', module_to_check, migration_to_check)

            # Here you can check how the module works before apply_postponed
            ...

            # Check whether the indexes applied properly. The `-x` parameter
            # causes exception on errors
            call_command('apply_postponed', 'run', '-x')
```

## Django settings

### `POSTPONE_INDEX_IGNORE`

The setting totally switches off the functionality of the package.

Always use this setting in the test environment to avoid using postponed index creation for the test database.

May be used in a heterogeneous database environment to switch off the package functionality on unsupported databases.

### `POSTPONE_INDEX_ADMIN_IGNORE`

The `PostponedSQL` model admin view is switched on by default. You can totally switch it off,
or create your own admin class instead. Use `postpone_index.admin.PostponedSQLAdminMixin` as a base class if necessary.

## Django database

The Django supports heterogeneous database environment in a single project. Every single database has it's own
state of migrations executed by the `manage.py migrate --database <alias>`.

The `apply_postponed` command also supports selection of the database alias using similar syntax:

```bash

# The 'default' database alias is used as a default
python manage.py migrate
python manage.py apply_postponed

# A non-default database alias parameter has similar syntax
python manage.py migrate --database another-postgres-database
python manage.py apply_postponed --database another-postgres-database
```

Use `POSTPONE_INDEX_IGNORE=1` environment to switch off the package functionality on migrations running on unsupported database engines like:

```bash
POSTPONE_INDEX_IGNORE=1 python manage.py migrate --database non-postgres-database
```

## Special migrations to avoid postpone index

Sometimes you may need to avoid the `postpone_index` applied to a single migration.

Just include the `PostponeIndexIgnoreMigrationMixin` into a base class list for your special migration:

```python
from django.db import migrations, models
from postpone_index.migration_utils import PostponeIndexIgnoreMigrationMixin

class Migration(PostponeIndexIgnoreMigrationMixin, migrations.Migration):
    ...
```
