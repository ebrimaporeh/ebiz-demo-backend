from django.db import models


class SectorNode(models.Model):
    code       = models.CharField(max_length=20, unique=True, db_index=True)
    name       = models.CharField(max_length=150)
    parent     = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'taxonomy_sectors'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'

    @property
    def depth(self):
        """Number of dashes in the code indicates hierarchy depth."""
        return self.code.count('-')


class GeographyNode(models.Model):
    LEVEL_CHOICES = [
        ('country',    'Country'),
        ('region',     'Region / LGA'),
        ('district',   'District'),
        ('settlement', 'Settlement'),
    ]

    code       = models.CharField(max_length=30, unique=True, db_index=True)
    name       = models.CharField(max_length=150)
    level      = models.CharField(max_length=20, choices=LEVEL_CHOICES, db_index=True)
    parent     = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'taxonomy_geographies'
        ordering = ['code']
        verbose_name_plural = 'Geography nodes'

    def __str__(self):
        return f'{self.code} — {self.name} ({self.level})'
