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
