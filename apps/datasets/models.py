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
