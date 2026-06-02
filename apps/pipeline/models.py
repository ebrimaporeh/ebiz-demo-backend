import uuid
from django.conf import settings
from django.db import models


class ValidationRun(models.Model):
    """
    Records every validation event (manual or AI) against a dataset.
    Stores per-row results and overall quality score.
    """
    VALIDATION_TYPE_CHOICES = [
        ('manual', 'Manual'),
        ('ai',     'AI-Assisted'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset         = models.ForeignKey(
        'datasets.Dataset', on_delete=models.CASCADE, related_name='validation_runs',
    )
    run_by          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='validation_runs',
    )
    run_at          = models.DateTimeField(auto_now_add=True, db_index=True)
    validation_type = models.CharField(max_length=10, choices=VALIDATION_TYPE_CHOICES, default='manual')
    quality_score   = models.FloatField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    # JSON arrays: [{row_index, status, message}, ...]
    row_results     = models.JSONField(null=True, blank=True)
    # JSON array: [{type, text}, ...]
    findings        = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'pipeline_validation_runs'
        ordering = ['-run_at']

    def __str__(self):
        label = self.run_at.strftime('%Y-%m-%d %H:%M') if self.run_at else '—'
        return f'{self.dataset.name} | {self.validation_type} | {label}'
