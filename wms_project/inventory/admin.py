
# wms_project/inventory/admin.py
from django.contrib import admin
from .models import Category, Product, Inventory, InventoryMovement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'cost_price', 'selling_price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'sku', 'barcode')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'min_quantity', 'reorder_level', 'last_restock_date')
    list_filter = ('warehouse', 'last_restock_date')
    search_fields = ('product__name', 'warehouse__name')

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'movement_type', 'quantity', 'reference', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('inventory__product__name', 'reference', 'notes')