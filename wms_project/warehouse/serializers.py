from rest_framework import serializers
from .models import Warehouse, Zone, Location
from inventory.models import Inventory

class WarehouseSerializer(serializers.ModelSerializer):
    manager_name = serializers.ReadOnlyField(source='manager.get_full_name')
    zone_count = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'address', 'city', 'state', 'country', 'postal_code', 
                  'phone', 'email', 'manager', 'manager_name', 'is_active',
                  'zone_count', 'location_count', 'created_at', 'updated_at']
    
    def get_zone_count(self, obj):
        return obj.zones.count()
    
    def get_location_count(self, obj):
        return obj.locations.count()

class ZoneSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    location_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Zone
        fields = ['id', 'warehouse', 'warehouse_name', 'name', 'description', 
                  'is_active', 'location_count', 'created_at', 'updated_at']
    
    def get_location_count(self, obj):
        return obj.locations.count()

class LocationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    zone_name = serializers.ReadOnlyField(source='zone.name')
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'warehouse', 'warehouse_name', 'zone', 'zone_name', 'name',
                  'barcode', 'aisle', 'rack', 'shelf', 'bin', 'is_active',
                  'product_count', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        # This would need to be updated based on how products are linked to locations
        # Currently, our model does not have a direct link between inventory and locations
        return 0