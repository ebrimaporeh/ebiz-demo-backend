"""
python manage.py setup_storage

Creates the Supabase Storage bucket (gambih-files) and verifies the connection.
Requires SUPABASE_SERVICE_ROLE_KEY to be set in .env.
"""
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initialise Supabase Storage buckets for this project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only check whether the bucket exists; do not create.',
        )

    def handle(self, *args, **options):
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            self.stderr.write(self.style.ERROR(
                'SUPABASE_SERVICE_ROLE_KEY is not set in .env\n'
                'Get it from: Supabase Dashboard → Project Settings → API → service_role'
            ))
            return

        from apps.storage_service import storage

        if options['check']:
            exists = storage.bucket_exists()
            if exists:
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Bucket '{settings.SUPABASE_BUCKET_NAME}' exists and is reachable."
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"✗ Bucket '{settings.SUPABASE_BUCKET_NAME}' not found. "
                    f"Run without --check to create it."
                ))
            return

        self.stdout.write('Setting up Supabase Storage buckets…')
        results = storage.setup_buckets()

        for bucket_name, status in results.items():
            if status == 'created':
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created bucket: {bucket_name}'))
            elif status == 'already_exists':
                self.stdout.write(f'  · Bucket already exists: {bucket_name}')
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ {bucket_name}: {status}'))

        self.stdout.write('')
        self.stdout.write(f'Storage URL: {settings.SUPABASE_URL}/storage/v1/')
        self.stdout.write(
            f'Public base: {settings.SUPABASE_URL}'
            f'/storage/v1/object/public/{settings.SUPABASE_BUCKET_NAME}/'
        )
        self.stdout.write(self.style.SUCCESS('\nDone. Run --check to verify.'))
