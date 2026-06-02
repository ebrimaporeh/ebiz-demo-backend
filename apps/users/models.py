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

# Maps each role to its allowed platform permissions — mirrors the prototype
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
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email       = models.EmailField(unique=True)
    name        = models.CharField(max_length=150)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', db_index=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table       = 'users'
        verbose_name   = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.name} <{self.email}> [{self.role}]'

    def get_platform_permissions(self):
        """Return the list of platform-level permission strings for this user's role."""
        return ROLE_PERMISSIONS.get(self.role, [])

    def has_platform_permission(self, permission):
        return permission in self.get_platform_permissions()
