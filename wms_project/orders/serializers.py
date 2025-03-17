from rest_framework import serializers
from .models import (Supplier, Customer, PurchaseOrder, PurchaseOrderItem,
                     SalesOrder, SalesOrderItem)

class SupplierSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address',
                 'city', 'state', 'country', 'postal_code', 'website', 'notes',
                 'is_active', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address',
                 'city', 'state', 'country', 'postal_code', 'notes',
                 'is_active', 'created_at', 'updated_at']

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'purchase_order', 'product', 'product_name', 'quantity',
                 'received_quantity', 'unit_price', 'tax_rate', 'subtotal',
                 'notes', 'created_at', 'updated_at']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.username')
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'supplier_name', 'warehouse',
                 'warehouse_name', 'status', 'order_date', 'expected_delivery_date',
                 'actual_delivery_date', 'shipping_address', 'shipping_method',
                 'tracking_number', 'subtotal', 'tax', 'shipping_cost', 'total',
                 'notes', 'created_by', 'created_by_name', 'approved_by',
                 'approved_by_name', 'items', 'created_at', 'updated_at']

class SalesOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = SalesOrderItem
        fields = ['id', 'sales_order', 'product', 'product_name', 'quantity',
                 'unit_price', 'tax_rate', 'discount', 'subtotal',
                 'notes', 'created_at', 'updated_at']

class SalesOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    processed_by_name = serializers.ReadOnlyField(source='processed_by.username')
    items = SalesOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = SalesOrder
        fields = ['id', 'order_number', 'customer', 'customer_name', 'warehouse',
                 'warehouse_name', 'status', 'order_date', 'shipping_address',
                 'shipping_method', 'tracking_number', 'shipping_date',
                 'delivery_date', 'subtotal', 'tax', 'shipping_cost', 'discount',
                 'total', 'notes', 'created_by', 'created_by_name',
                 'processed_by', 'processed_by_name', 'items', 'created_at', 'updated_at']