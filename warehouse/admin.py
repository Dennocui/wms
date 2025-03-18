from django.contrib import admin
from .models import Warehouse, Zone, Location

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'manager', 'is_active', 'created_at')
    list_filter = ('is_active', 'country', 'state')
    search_fields = ('name', 'address', 'city', 'manager__username')

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'is_active', 'created_at')
    list_filter = ('warehouse', 'is_active')
    search_fields = ('name', 'warehouse__name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'zone', 'aisle', 'rack', 'shelf', 'bin', 'is_active')
    list_filter = ('warehouse', 'zone', 'is_active')
    search_fields = ('name', 'warehouse__name', 'zone__name', 'aisle', 'rack', 'shelf', 'bin')