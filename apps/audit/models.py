import uuid
from django.conf import settings
from django.db import models

ACTION_CHOICES = [
    ('record_ingested',   'Record Ingested'),
    ('batch_ingested',    'Batch Ingested'),
    ('validation_run',    'Validation Run'),
    ('record_promoted',   'Record Promoted'),
    ('dataset_created',   'Dataset Created'),
    ('dataset_published', 'Dataset Published'),
    ('dataset_archived',  'Dataset Archived'),
    ('version_created',   'Version Created'),
    ('record_corrected',  'Record Corrected'),
    ('taxonomy_updated',  'Taxonomy Updated'),
    ('access_granted',    'Access Granted'),
    ('access_revoked',    'Access Revoked'),
    ('user_login',        'User Login'),
    ('user_logout',       'User Logout'),
    ('permission_changed','Permission Changed'),
]


class AuditEntry(models.Model):
    """
    Append-only audit log.  save() blocks updates — every mutation in the
    system must write a new entry.  Never delete rows in production.
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp   = models.DateTimeField(auto_now_add=True, db_index=True)
    actor       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='audit_entries',
    )
    actor_role  = models.CharField(max_length=20, blank=True)
    action      = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id   = models.CharField(max_length=100, blank=True, db_index=True)
    entity_name = models.CharField(max_length=255, blank=True)
    layer       = models.CharField(max_length=10, null=True, blank=True)
    system      = models.CharField(max_length=20, default='staff')
    details     = models.JSONField(default=dict)
    before_state = models.JSONField(null=True, blank=True)
    after_state  = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']

    def __str__(self):
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else '—'
        return f'{ts} | {self.actor_role} | {self.action} | {self.entity_name}'

    def save(self, *args, **kwargs):
        if self.pk and AuditEntry.objects.filter(pk=self.pk).exists():
            raise ValueError('AuditEntry records are immutable — no updates allowed.')
        super().save(*args, **kwargs)
