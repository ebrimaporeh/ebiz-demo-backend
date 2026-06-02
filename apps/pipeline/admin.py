from django.contrib import admin
from .models import ValidationRun

@admin.register(ValidationRun)
class ValidationRunAdmin(admin.ModelAdmin):
    list_display    = ('dataset', 'validation_type', 'quality_score', 'run_by', 'run_at')
    list_filter     = ('validation_type',)
    search_fields   = ('dataset__name',)
    ordering        = ('-run_at',)
    readonly_fields = ('run_at',)
