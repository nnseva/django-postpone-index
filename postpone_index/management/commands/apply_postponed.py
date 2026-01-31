"""
The apply_postponed command applies collected postponed index and constraint creation
in CONCURRENTLY manner.
"""
import argparse
import logging
import sys

from django.core.management.base import BaseCommand
from django.db import connections

from postpone_index.models import PostponedSQL
from postpone_index.utils import ObjMap, Utils


logger = logging.getLogger(__name__)


class Command(Utils, BaseCommand):
    __doc__ = __doc__
    help = __doc__

    _short_format = '%(d)s %(sql)s'
    _descr_format = '%(i)04d: %(d)s %(description)s'
    _long_format = '%(i)04d: %(d)s %(sql)s'

    class formatter_class(argparse.RawTextHelpFormatter):
        pass

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title='Commands',
            dest='command',
            help='Use --help with command to see the command-specific help',
        )
        show = subparsers.add_parser(
            name='list',
            formatter_class=self.formatter_class,
            help='Show applied and not yet applied postponed index creation jobs'
        )
        show.add_argument(
            '-db', '--database',
            dest='database',
            default='default',
            help='Database alias to be applied, default is %(default)s'
        )
        show.add_argument(
            '-r', '--reversed',
            dest='reversed',
            action='store_true',
            help='Show records in reversed order'
        )
        show.add_argument(
            '-u', '--unapplied',
            dest='unapplied',
            action='store_true',
            help='Show only unapplied records'
        )
        show.add_argument(
            '-e', '--erroneous',
            dest='erroneous',
            action='store_true',
            help='Show only erroneous records having non-null error'
        )
        show.add_argument(
            '-f', '--format',
            dest='format',
            default='s',
            help=f'''Output format. Use either:
    - `s` for short SQL-only format `{self._short_format}` (default)
    - `d` for enumerated descriptions format `{self._descr_format}`
    - `l` for enumerated SQL format `{self._long_format}`
    - %-style named format
Use the PostponedSQL field names for %-style format.
Additional names are:
    - `i` for enumeration index
    - `d` for the `done` attribute in form of `+` or `-`'''.replace('%', '%%')
        )
        run = subparsers.add_parser(
            name='run',
            formatter_class=self.formatter_class,
            help='Apply not yet applied postponed index creation jobs'
        )
        run.add_argument(
            '-x', '--exception',
            dest='exception',
            action='store_true',
            help='Immediately stop on any exception. Continues with the next job by default'
        )
        run.add_argument(
            '-db', '--database',
            dest='database',
            default='default',
            help='Database alias to be applied, default is %(default)s'
        )
        cleanup = subparsers.add_parser(
            name='cleanup',
            formatter_class=self.formatter_class,
            help='Cleanup stored applied index creation jobs'
        )
        cleanup.add_argument(
            '--all',
            dest='all',
            action='store_true',
            help='Cleanup all postponed SQL including not yet applied. Be careful!'
        )
        cleanup.add_argument(
            '-db', '--database',
            dest='database',
            default='default',
            help='Database alias to be applied, default is %(default)s'
        )

    def handle(self, *args, **options):
        """Handling commands"""
        if not options['command']:
            return self.print_help(sys.argv[0], sys.argv[1])
        return getattr(self, '_handle_%s' % options['command'])(*args, **options)

    def _handle_list(self, *args, **options):
        """Handle list command"""
        try:
            PostponedSQL.objects.using(options['database']).all().first()
        except Exception:
            # The table has not been created
            return

        q = PostponedSQL.objects.using(options['database']).all()
        q = q.order_by('-ts' if options['reversed'] else 'ts')
        if options['unapplied']:
            q = q.filter(done=False)
        if options['erroneous']:
            q = q.filter(error__isnull=False)
        match options['format']:
            case 's':
                format = self._short_format
            case 'd':
                format = self._descr_format
            case 'l':
                format = self._long_format
            case _:
                format = options['format']
        for i, j in enumerate(q):
            print(format % ObjMap(j, {
                'i': i,
            }))

    def _handle_run(self, *args, **options):
        """Handle run command"""
        try:
            PostponedSQL.objects.using(options['database']).all().first()
        except Exception:
            # The table has not been created
            return
        q = PostponedSQL.objects.using(options['database']).filter(done=False).order_by('ts')
        for j in q:
            try:
                j.error = None
                j.done = False
                self._handle_run_job(j, *args, **options)
                j.save(update_fields=['error', 'done'])
            except Exception as ex:
                logger.warning('Error on running job: %s', ex)
                if not j.error:
                    j.error = 'Exception: %s' % ex
                j.save(update_fields=['error', 'done'])
                if options['exception']:
                    raise

    def _handle_cleanup(self, *args, **options):
        """Handle cleanup command"""
        try:
            PostponedSQL.objects.using(options['database']).all().first()
        except Exception:
            # The table has not been created
            return
        q = PostponedSQL.objects.using(options['database'])
        if not options['all']:
            q = q.filter(done=True)
        q.delete()

    def _handle_run_job(self, job, *args, **options):
        """Handle a single job for the run command"""
        if match := self._create_index_re.fullmatch(job.sql):
            unique = match.group('unique') or ''
            index_name = match.group('index_nameq') or match.group('index_name')
            table_name = match.group('table_nameq') or match.group('table_name')
            rest = match.group('rest')
            sql = 'DROP INDEX IF EXISTS "%s"' % (
                index_name,
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
            sql = 'CREATE %sINDEX CONCURRENTLY "%s" ON "%s" %s' % (
                unique,
                index_name,
                table_name,
                rest
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
        elif match := self._add_constraint_re.fullmatch(job.sql):
            unique = 'UNIQUE '
            index_name = match.group('index_nameq') or match.group('index_name')
            table_name = match.group('table_nameq') or match.group('table_name')
            rest = match.group('rest')
            sql = 'ALTER TABLE "%s" DROP CONSTRAINT IF EXISTS "%s"' % (
                table_name,
                index_name,
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
            sql = 'DROP INDEX IF EXISTS "%s"' % (
                index_name,
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
            sql = 'CREATE %sINDEX CONCURRENTLY "%s" ON "%s" %s' % (
                unique,
                index_name,
                table_name,
                rest
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
            sql = 'ALTER TABLE "%s" ADD CONSTRAINT "%s" UNIQUE USING INDEX "%s"' % (
                table_name,
                index_name,
                index_name,
            )
            logger.info('[%s] SQL: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
        else:
            logger.info('[%s] Unrecognized: %s', options['database'], sql)
            cursor = connections[options['database']].cursor()
            cursor.execute(sql)
            cursor.close()
        job.error = None
        job.done = True
