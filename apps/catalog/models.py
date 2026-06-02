import uuid
from django.conf import settings
from django.db import models

ACCESS_TIER_CHOICES = [
    ('public_free', 'Public Free'),
    ('researcher',  'Researcher'),
    ('api',         'API'),
    ('enterprise',  'Enterprise'),
]

STATUS_CHOICES = [
    ('draft',     'Draft'),
    ('in_review', 'In Review'),
    ('published', 'Published'),
    ('archived',  'Archived'),
]


class PublishedDataset(models.Model):
    """
    A curated, publishable data product composed of one or more Gold-layer datasets.
    Appears on the public Browse / Catalog pages when status = 'published'.
    """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    methodology  = models.TextField(blank=True)
    license      = models.CharField(max_length=50, default='CC BY 4.0')
    access_tier  = models.CharField(max_length=20, choices=ACCESS_TIER_CHOICES, default='public_free')
    version      = models.CharField(max_length=10, default='0.1')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    quality_score = models.FloatField(null=True, blank=True)

    geographic_scope = models.ManyToManyField(
        'taxonomy.GeographyNode', blank=True, related_name='catalog_datasets',
    )
    sector_scope = models.ManyToManyField(
        'taxonomy.SectorNode', blank=True, related_name='catalog_datasets',
    )
    records = models.ManyToManyField(
        'datasets.Dataset', blank=True, related_name='catalog_appearances',
    )

    download_count = models.PositiveIntegerField(default=0)

    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_catalog_datasets',
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='published_catalog_datasets',
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_datasets'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} (v{self.version}) [{self.status}]'


class DatasetVersion(models.Model):
    """Immutable changelog entry — one row per version bump."""
    published_dataset = models.ForeignKey(
        PublishedDataset, on_delete=models.CASCADE, related_name='version_history',
    )
    version    = models.CharField(max_length=10)
    date       = models.DateField(auto_now_add=True)
    notes      = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='dataset_versions',
    )

    class Meta:
        db_table = 'catalog_dataset_versions'
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.published_dataset.title} — v{self.version}'
