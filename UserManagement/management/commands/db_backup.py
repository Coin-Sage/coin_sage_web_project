from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Backup PG database using pg_dump.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', nargs='?', type=str,
            default=f'{settings.BASE_DIR}/db_backups',
            help='Path to output directory for the backup.'
        )
        parser.add_argument(
            '--db_name', nargs='?', type=str,
            help='Database name for backup.'
        )
        parser.add_argument(
            '--db_user', nargs='?', type=str,
            default=None,
            help='Username for the database.'
        )
        parser.add_argument(
            '--db_password', nargs='?', type=str,
            default=None,
            help='Password for the database.'
        )

    def handle(self, *args, **options):
        output_path = options['output']
        db_name = options['db_name'] or settings.DATABASES['default']['NAME']
        db_user = options['db_user'] or settings.DATABASES['default']['USER']
        db_password = (
            options['db_password']
            or settings.DATABASES['default']['PASSWORD']
        )

        os.makedirs(output_path, exist_ok=True)

        if db_password:
            os.environ['PGPASSWORD'] = db_password  # Delete in production
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            file_name = f"{db_name}_{timestamp}.sql"
            file_path = os.path.join(output_path, f"{file_name}")

            command = f"pg_dump -U {db_user} -d {db_name} -f {file_path}"

            self.stdout.write(self.style.SUCCESS(
                f"Starting backup of database {db_name} to {file_path}..."
            ))

            subprocess.run(command, shell=True)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully backed up database to {file_path}."
            ))