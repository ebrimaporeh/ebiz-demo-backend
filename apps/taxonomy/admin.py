from django.contrib import admin
from .models import SectorNode, GeographyNode

@admin.register(SectorNode)
class SectorNodeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'parent', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('code', 'name')
    ordering      = ('code',)

@admin.register(GeographyNode)
class GeographyNodeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'level', 'parent', 'is_active')
    list_filter   = ('level', 'is_active')
    search_fields = ('code', 'name')
    ordering      = ('code',)
