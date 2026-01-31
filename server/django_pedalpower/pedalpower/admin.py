from django.contrib import admin
from .models import Telemetry


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'server_timestamp', 'voltage', 'current', 'power', 'sequence_number']
    list_filter = ['device_id', 'server_timestamp']
    search_fields = ['device_id']
    ordering = ['-server_timestamp']
    date_hierarchy = 'server_timestamp'
    
    # Read-only since table is managed externally
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
