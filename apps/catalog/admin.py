from django.contrib import admin
from .models import PublishedDataset, DatasetVersion

class DatasetVersionInline(admin.TabularInline):
    model  = DatasetVersion
    extra  = 0
    fields = ('version', 'date', 'notes', 'created_by')
    readonly_fields = ('date',)

@admin.register(PublishedDataset)
class PublishedDatasetAdmin(admin.ModelAdmin):
    list_display      = ('title', 'version', 'status', 'access_tier', 'quality_score', 'published_at')
    list_filter       = ('status', 'access_tier')
    search_fields     = ('title',)
    ordering          = ('-created_at',)
    inlines           = [DatasetVersionInline]
    readonly_fields   = ('created_at', 'last_updated')
    filter_horizontal = ('records', 'sector_scope', 'geographic_scope')
