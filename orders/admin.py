from django.contrib import admin
from .models import (Supplier, Customer, PurchaseOrder, PurchaseOrderItem,
                     SalesOrder, SalesOrderItem)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'country', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'contact_person', 'email', 'phone')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'country', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'contact_person', 'email', 'phone')

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('product', 'quantity', 'received_quantity', 'unit_price', 'tax_rate')
    raw_id_fields = ('product',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'warehouse', 'status', 'order_date', 'total')
    list_filter = ('status', 'order_date', 'warehouse')
    search_fields = ('po_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ('created_by', 'approved_by', 'subtotal', 'total')

class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'discount')
    raw_id_fields = ('product',)

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'warehouse', 'status', 'order_date', 'total')
    list_filter = ('status', 'order_date', 'warehouse')
    search_fields = ('order_number', 'customer__name')
    inlines = [SalesOrderItemInline]
    readonly_fields = ('created_by', 'processed_by', 'subtotal', 'total')