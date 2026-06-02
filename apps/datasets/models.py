"""
Dataset pipeline models.

Files attached to datasets (raw uploads, exported reports, etc.) are stored in
Supabase Storage.  The public URL is saved in DatasetFile.file_url.

Upload example (in a view/serializer):
    from apps.storage_service import storage

    path = storage.dataset_file_path(str(dataset.id), uploaded_file.name)
    url  = storage.upload(path, uploaded_file.read(), uploaded_file.content_type)

    DatasetFile.objects.create(
        dataset=dataset,
        file_name=uploaded_file.name,
        file_url=url,
        storage_path=path,
        file_size=uploaded_file.size,
        mime_type=uploaded_file.content_type,
        uploaded_by=request.user,
    )
"""
import uuid
from django.conf import settings
from django.db import models

DATA_TYPE_CHOICES = [
    ('time_series',     'Time Series'),
    ('cross_sectional', 'Cross-Sectional'),
    ('panel',           'Panel / Longitudinal'),
    ('administrative',  'Administrative'),
    ('survey',          'Survey'),
    ('geospatial',      'Geospatial'),
]

FREQUENCY_CHOICES = [
    ('daily',     'Daily'),
    ('weekly',    'Weekly'),
    ('monthly',   'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annual',    'Annual'),
]

LAYER_CHOICES = [
    ('bronze', 'Bronze'),
    ('silver', 'Silver'),
    ('gold',   'Gold'),
]

COLUMN_TYPE_CHOICES = [
    ('text',       'Text'),
    ('number',     'Number'),
    ('percentage', 'Percentage'),
    ('currency',   'Currency'),
    ('date',       'Date'),
    ('boolean',    'Boolean'),
]


class Dataset(models.Model):
    """
    A dataset ingested into the pipeline.
    Progresses through Bronze → Silver → Gold via validation and promotion.
    Each dataset holds an arbitrary number of typed rows (see DatasetRow).
    """
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name             = models.CharField(max_length=255)
    data_type        = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES, db_index=True)
    source_org       = models.CharField(max_length=255)
    collector_name   = models.CharField(max_length=150, blank=True)
    collection_date  = models.DateField()
    ref_period_start = models.DateField(null=True, blank=True)
    ref_period_end   = models.DateField(null=True, blank=True)
    frequency        = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, null=True, blank=True)
    unit             = models.CharField(max_length=100, blank=True)
    description      = models.TextField(blank=True)
    methodology      = models.TextField(blank=True)
    license          = models.CharField(max_length=50, default='CC BY 4.0')

    # Pipeline state
    layer         = models.CharField(max_length=10, choices=LAYER_CHOICES, default='bronze', db_index=True)
    version       = models.PositiveIntegerField(default=1)
    quality_score = models.FloatField(null=True, blank=True)
    provenance_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Taxonomy scope (many-to-many — a dataset can span multiple sectors/geographies)
    sector_scope    = models.ManyToManyField('taxonomy.SectorNode',    blank=True, related_name='datasets')
    geography_scope = models.ManyToManyField('taxonomy.GeographyNode', blank=True, related_name='datasets')

    # Lifecycle actors
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='submitted_datasets',
    )
    submitted_at     = models.DateTimeField(auto_now_add=True)
    validated_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='validated_datasets',
    )
    validated_at     = models.DateTimeField(null=True, blank=True)
    validation_notes = models.TextField(blank=True)
    promoted_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='promoted_datasets',
    )
    promoted_at = models.DateTimeField(null=True, blank=True)

    # Gold-only enrichment fields
    sector_benchmark = models.JSONField(null=True, blank=True)
    percentile_rank  = models.FloatField(null=True, blank=True)

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'datasets'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'[{self.layer.upper()}] {self.name}'

    @property
    def row_count(self):
        return self.rows.count()


class DatasetColumn(models.Model):
    """Schema definition for a dataset — one row per column."""
    dataset   = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='columns')
    key       = models.CharField(max_length=100)
    label     = models.CharField(max_length=200)
    data_type = models.CharField(max_length=20, choices=COLUMN_TYPE_CHOICES, default='text')
    required  = models.BooleanField(default=False)
    order     = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table      = 'dataset_columns'
        ordering      = ['order']
        unique_together = [['dataset', 'key']]

    def __str__(self):
        return f'{self.dataset.name} → {self.label} ({self.data_type})'


class DatasetRow(models.Model):
    """A single data row stored as a JSON object keyed by column keys."""
    dataset   = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='rows')
    row_index = models.PositiveIntegerField()
    data      = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table      = 'dataset_rows'
        ordering      = ['row_index']
        unique_together = [['dataset', 'row_index']]

    def __str__(self):
        return f'{self.dataset.name} — row {self.row_index}'


FILE_KIND_CHOICES = [
    ('raw',        'Raw Upload (CSV / Excel)'),
    ('attachment', 'Attachment (PDF, doc, etc.)'),
    ('export',     'Exported Report'),
]


class DatasetFile(models.Model):
    """
    A file attached to a dataset, stored in Supabase Storage.

    `file_url` is the public URL returned by storage_service.storage.upload().
    `storage_path` is the path inside the bucket (needed to delete the file later).

    Folder layout inside the bucket:
        datasets/{dataset.id}/files/   ← attachments / exports
        datasets/{dataset.id}/raw/     ← original uploaded CSV / Excel
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset      = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='files')
    kind         = models.CharField(max_length=20, choices=FILE_KIND_CHOICES, default='attachment')
    file_name    = models.CharField(max_length=255, help_text='Original filename')
    file_url     = models.URLField(
        max_length=500,
        help_text='Public URL in Supabase Storage — returned by storage_service.storage.upload()',
    )
    storage_path = models.CharField(
        max_length=500,
        help_text='Path inside the bucket — required to delete the file',
    )
    file_size    = models.PositiveIntegerField(null=True, blank=True, help_text='Bytes')
    mime_type    = models.CharField(max_length=100, blank=True)
    uploaded_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='uploaded_dataset_files',
    )
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dataset_files'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.dataset.name} → {self.file_name}'

    def delete_from_storage(self) -> None:
        """Remove the file from Supabase Storage then delete this record."""
        from apps.storage_service import storage
        storage.delete(self.storage_path)
        self.delete()

    def size_display(self) -> str:
        if not self.file_size:
            return '—'
        for unit in ('B', 'KB', 'MB', 'GB'):
            if self.file_size < 1024:
                return f'{self.file_size:.1f} {unit}'
            self.file_size /= 1024
        return f'{self.file_size:.1f} TB'
