"""
Supabase Storage service — used by all apps that need to upload or delete files.

Every file that ends up in Supabase Storage gets a public URL stored directly
in a model URLField.  No django-storages FileField abstraction is used here;
uploads are explicit and the returned URL is what gets saved to the DB.

Public URL pattern:
  {SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}

Usage:
    from apps.storage_service import storage

    url = storage.upload(path='avatars/user-id/avatar.jpg', data=file_bytes, mime='image/jpeg')
    storage.delete(path='avatars/user-id/avatar.jpg')
    storage.setup_buckets()          # run once, or via management command
"""

import mimetypes
import uuid
from pathlib import PurePosixPath

from django.conf import settings


def _get_client():
    from supabase import create_client
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


class SupabaseStorageService:
    """Thin wrapper around the Supabase storage client."""

    def __init__(self):
        self.bucket   = settings.SUPABASE_BUCKET_NAME
        self.base_url = (
            f"{settings.SUPABASE_URL}"
            f"/storage/v1/object/public/{self.bucket}"
        )

    # ── Public helpers ─────────────────────────────────────────────────────

    def public_url(self, path: str) -> str:
        """Build the public URL for a given storage path (no upload)."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def upload(self, path: str, data: bytes, mime: str | None = None) -> str:
        """
        Upload bytes to `path` in the default bucket.
        Returns the public URL stored in the model field.

        path examples:
            avatars/{user_id}/avatar.jpg
            datasets/{dataset_id}/files/report.pdf
        """
        if not mime:
            mime, _ = mimetypes.guess_type(path)
            mime = mime or 'application/octet-stream'

        client = _get_client()
        client.storage.from_(self.bucket).upload(
            path=path,
            file=data,
            file_options={'content-type': mime, 'upsert': 'true'},
        )
        return self.public_url(path)

    def delete(self, path: str) -> None:
        """Remove a file from storage (safe to call even if file doesn't exist)."""
        try:
            _get_client().storage.from_(self.bucket).remove([path])
        except Exception:
            pass

    # ── Path builders ──────────────────────────────────────────────────────

    @staticmethod
    def avatar_path(user_id: str, filename: str) -> str:
        ext  = PurePosixPath(filename).suffix or '.jpg'
        return f"avatars/{user_id}/avatar{ext}"

    @staticmethod
    def dataset_file_path(dataset_id: str, filename: str) -> str:
        slug = PurePosixPath(filename).name
        return f"datasets/{dataset_id}/files/{slug}"

    @staticmethod
    def dataset_raw_path(dataset_id: str, filename: str) -> str:
        slug = PurePosixPath(filename).name
        return f"datasets/{dataset_id}/raw/{slug}"

    # ── Bucket initialisation ──────────────────────────────────────────────

    def setup_buckets(self) -> dict:
        """
        Create required buckets if they don't exist.
        Called by: python manage.py setup_storage
        Requires SUPABASE_SERVICE_ROLE_KEY to be set.
        """
        client   = _get_client()
        results  = {}
        buckets  = [
            {'id': self.bucket, 'public': True},
        ]
        for spec in buckets:
            name = spec['id']
            try:
                client.storage.create_bucket(
                    name,
                    options={'public': spec['public']},
                )
                results[name] = 'created'
            except Exception as exc:
                msg = str(exc).lower()
                if 'already exists' in msg or 'duplicate' in msg:
                    results[name] = 'already_exists'
                else:
                    results[name] = f'error: {exc}'
        return results

    def bucket_exists(self) -> bool:
        try:
            buckets = _get_client().storage.list_buckets()
            return any(b.id == self.bucket for b in buckets)
        except Exception:
            return False


# Module-level singleton — import and use directly
storage = SupabaseStorageService()
