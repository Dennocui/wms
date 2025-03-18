from rest_framework import serializers
from .models import Category, Product, Inventory, InventoryMovement

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'sku', 'barcode',
                  'weight', 'height', 'width', 'length', 'cost_price', 'selling_price',
                  'image', 'total_quantity', 'created_at', 'updated_at']
    
    def get_total_quantity(self, obj):
        return sum(inv.quantity for inv in obj.inventory.all())

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'warehouse', 'warehouse_name', 'quantity',
                  'min_quantity', 'max_quantity', 'reorder_level', 'last_restock_date',
                  'created_at', 'updated_at']

class InventoryMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='inventory.product.name')
    warehouse_name = serializers.ReadOnlyField(source='inventory.warehouse.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'inventory', 'product_name', 'warehouse_name', 'movement_type',
                  'quantity', 'reference', 'notes', 'created_by', 'created_by_username',
                  'created_at']