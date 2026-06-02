from django.contrib import admin
from .models import Dataset, DatasetColumn, DatasetRow

class DatasetColumnInline(admin.TabularInline):
    model  = DatasetColumn
    extra  = 0
    fields = ('key', 'label', 'data_type', 'required', 'order')

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display    = ('name', 'data_type', 'layer', 'source_org', 'quality_score', 'submitted_at')
    list_filter     = ('layer', 'data_type')
    search_fields   = ('name', 'source_org', 'provenance_id')
    ordering        = ('-submitted_at',)
    inlines         = [DatasetColumnInline]
    readonly_fields = ('submitted_at', 'provenance_id')

@admin.register(DatasetRow)
class DatasetRowAdmin(admin.ModelAdmin):
    list_display   = ('dataset', 'row_index', 'created_at')
    raw_id_fields  = ('dataset',)
    ordering       = ('dataset', 'row_index')

from .models import DatasetFile

@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display  = ('dataset', 'file_name', 'kind', 'mime_type', 'file_size', 'uploaded_by', 'uploaded_at')
    list_filter   = ('kind',)
    search_fields = ('file_name', 'dataset__name')
    ordering      = ('-uploaded_at',)
    readonly_fields = ('uploaded_at', 'file_url', 'storage_path')
