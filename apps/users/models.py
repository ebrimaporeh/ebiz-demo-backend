"""
Custom User model.

Avatar images are stored in Supabase Storage.
The public URL is saved in `avatar_url` — use apps.storage_service.storage to upload.

Upload example (in a view/serializer):
    from apps.storage_service import storage

    path = storage.avatar_path(str(user.id), uploaded_file.name)
    url  = storage.upload(path, uploaded_file.read(), uploaded_file.content_type)
    user.avatar_url = url
    user.save(update_fields=['avatar_url'])
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

ROLE_CHOICES = [
    ('admin',      'Admin'),
    ('analyst',    'Analyst'),
    ('reviewer',   'Reviewer'),
    ('publisher',  'Publisher'),
    ('researcher', 'Researcher'),
    ('viewer',     'Viewer'),
]

# Role → allowed platform permissions (mirrors the prototype permission matrix)
ROLE_PERMISSIONS = {
    'admin': [
        'ingest_bronze', 'validate_silver', 'promote_gold', 'publish_dataset',
        'manage_taxonomy', 'manage_access', 'view_audit_log',
        'view_gold', 'view_silver', 'view_bronze',
    ],
    'analyst': [
        'ingest_bronze', 'validate_silver', 'view_audit_log',
        'view_gold', 'view_silver', 'view_bronze',
    ],
    'reviewer': [
        'validate_silver', 'promote_gold', 'view_audit_log',
        'view_gold', 'view_silver', 'view_bronze',
    ],
    'publisher': [
        'publish_dataset', 'view_audit_log',
        'view_gold', 'view_silver',
    ],
    'researcher': [
        'view_audit_log', 'view_gold', 'view_silver',
    ],
    'viewer': [
        'view_gold',
    ],
}


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role',         'admin')
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # ── Identity ──────────────────────────────────────────────────────────
    id    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name  = models.CharField(max_length=150)

    # ── Platform role ─────────────────────────────────────────────────────
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='viewer', db_index=True,
    )

    # ── Profile (stored in Supabase Storage, URL saved here) ──────────────
    avatar_url = models.URLField(
        max_length=500, blank=True, null=True,
        help_text=(
            'Public URL of the avatar image in Supabase Storage. '
            'Upload via apps.storage_service.storage.upload() and save the returned URL here.'
        ),
    )
    bio   = models.TextField(blank=True)
    phone = models.CharField(max_length=25, blank=True)

    # ── Django internals ──────────────────────────────────────────────────
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table            = 'users'
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.name} <{self.email}> [{self.role}]'

    # ── Platform permission helpers ────────────────────────────────────────

    def get_platform_permissions(self) -> list[str]:
        """Return the list of platform permission strings for this user's role."""
        return ROLE_PERMISSIONS.get(self.role, [])

    def has_platform_permission(self, permission: str) -> bool:
        return permission in self.get_platform_permissions()

    # ── Storage helpers ────────────────────────────────────────────────────

    def build_avatar_path(self, filename: str) -> str:
        """Return the Supabase Storage path for this user's avatar."""
        from apps.storage_service import storage
        return storage.avatar_path(str(self.id), filename)

    def delete_avatar(self) -> None:
        """Remove the avatar from Supabase Storage and clear the URL field."""
        if not self.avatar_url:
            return
        from apps.storage_service import storage
        # Extract path from the full public URL
        base = f"{storage.base_url}/"
        if self.avatar_url.startswith(base):
            path = self.avatar_url[len(base):]
            storage.delete(path)
        self.avatar_url = None
        self.save(update_fields=['avatar_url'])
