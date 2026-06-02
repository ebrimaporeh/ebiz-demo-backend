from django.contrib import admin
from .models import AuditEntry

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display    = ('timestamp', 'actor', 'actor_role', 'action', 'entity_name', 'layer', 'system')
    list_filter     = ('action', 'actor_role', 'layer', 'system')
    search_fields   = ('entity_name', 'entity_id', 'actor__name')
    ordering        = ('-timestamp',)
    readonly_fields = ('id', 'timestamp', 'actor', 'actor_role', 'action',
                       'entity_type', 'entity_id', 'entity_name',
                       'layer', 'system', 'details', 'before_state', 'after_state')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
