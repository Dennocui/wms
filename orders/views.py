from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (Supplier, Customer, PurchaseOrder, PurchaseOrderItem,
                     SalesOrder, SalesOrderItem)
from .serializers import (SupplierSerializer, CustomerSerializer,
                         PurchaseOrderSerializer, PurchaseOrderItemSerializer,
                         SalesOrderSerializer, SalesOrderItemSerializer)
from inventory.models import Inventory, InventoryMovement

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'contact_person', 'email', 'phone', 'city', 'country']
    
    @action(detail=True, methods=['get'])
    def purchase_orders(self, request, pk=None):
        supplier = self.get_object()
        purchase_orders = PurchaseOrder.objects.filter(supplier=supplier)
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'contact_person', 'email', 'phone', 'city', 'country']
    
    @action(detail=True, methods=['get'])
    def sales_orders(self, request, pk=None):
        customer = self.get_object()
        sales_orders = SalesOrder.objects.filter(customer=customer)
        serializer = SalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data)

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['po_number', 'supplier__name', 'warehouse__name', 'status']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        purchase_order = self.get_object()
               
        if purchase_order.status not in ['DRAFT', 'SUBMITTED']:
            return Response({'error': 'Cannot modify purchase order in current status'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PurchaseOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(purchase_order=purchase_order)
            purchase_order.update_totals()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        purchase_order = self.get_object()
        
        if purchase_order.status != 'SUBMITTED':
            return Response({'error': 'Only submitted purchase orders can be approved'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        purchase_order.status = 'APPROVED'
        purchase_order.approved_by = request.user
        purchase_order.save()
        
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        purchase_order = self.get_object()
        
        if purchase_order.status not in ['APPROVED', 'SHIPPED']:
            return Response({'error': 'Only approved or shipped purchase orders can be received'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Process received items
        received_items = request.data.get('items', [])
        for item_data in received_items:
            item_id = item_data.get('id')
            received_qty = item_data.get('received_quantity', 0)
            
            if not item_id or received_qty <= 0:
                continue
            
            try:
                po_item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=purchase_order)
                
                # Update received quantity
                remaining_qty = po_item.quantity - po_item.received_quantity
                if received_qty > remaining_qty:
                    received_qty = remaining_qty
                
                po_item.received_quantity += received_qty
                po_item.save()
                
                # Update inventory
                inventory, created = Inventory.objects.get_or_create(
                    product=po_item.product,
                    warehouse=purchase_order.warehouse,
                    defaults={'quantity': 0}
                )
                
                old_qty = inventory.quantity
                inventory.quantity += received_qty
                inventory.last_restock_date = timezone.now()
                inventory.save()
                
                # Create inventory movement record
                InventoryMovement.objects.create(
                    inventory=inventory,
                    movement_type='IN',
                    quantity=received_qty,
                    reference=f"PO #{purchase_order.po_number}",
                    notes=f"Received from PO #{purchase_order.po_number}",
                    created_by=request.user
                )
                
            except PurchaseOrderItem.DoesNotExist:
                continue
        
        # Mark PO as received if all items are fully received
        items = PurchaseOrderItem.objects.filter(purchase_order=purchase_order)
        all_received = all(item.received_quantity >= item.quantity for item in items)
        
        if all_received:
            purchase_order.status = 'RECEIVED'
            purchase_order.actual_delivery_date = timezone.now().date()
            purchase_order.save()
        
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)

class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        purchase_order = instance.purchase_order
        if purchase_order.status not in ['DRAFT', 'SUBMITTED']:
            raise serializers.ValidationError("Cannot delete item from purchase order in current status")
        instance.delete()
        purchase_order.update_totals()

class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all().order_by('-created_at')
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_number', 'customer__name', 'warehouse__name', 'status']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        sales_order = self.get_object()
        
        if sales_order.status not in ['DRAFT', 'SUBMITTED']:
            return Response({'error': 'Cannot modify sales order in current status'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SalesOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            # Check inventory availability
            product_id = serializer.validated_data['product'].id
            quantity = serializer.validated_data['quantity']
            warehouse_id = sales_order.warehouse.id
            
            inventory = Inventory.objects.filter(
                product_id=product_id,
                warehouse_id=warehouse_id
            ).first()
            
            if not inventory or inventory.quantity < quantity:
                return Response({'error': 'Insufficient inventory'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save(sales_order=sales_order)
            sales_order.update_totals()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        sales_order = self.get_object()
        
        if sales_order.status != 'SUBMITTED':
            return Response({'error': 'Only submitted sales orders can be processed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Check inventory availability for all items
        items = SalesOrderItem.objects.filter(sales_order=sales_order)
        warehouse_id = sales_order.warehouse.id
        
        for item in items:
            inventory = Inventory.objects.filter(
                product=item.product,
                warehouse_id=warehouse_id
            ).first()
            
            if not inventory or inventory.quantity < item.quantity:
                return Response({
                    'error': f'Insufficient inventory for {item.product.name}',
                    'available': inventory.quantity if inventory else 0,
                    'required': item.quantity
                }, status=status.HTTP_400_BAD_REQUEST)
        
        sales_order.status = 'PROCESSING'
        sales_order.processed_by = request.user
        sales_order.save()
        
        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        sales_order = self.get_object()
        
        if sales_order.status not in ['PACKED']:
            return Response({'error': 'Only packed orders can be shipped'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        tracking_number = request.data.get('tracking_number')
        shipping_method = request.data.get('shipping_method')
        
        if tracking_number:
            sales_order.tracking_number = tracking_number
        
        if shipping_method:
            sales_order.shipping_method = shipping_method
        
        sales_order.status = 'SHIPPED'
        sales_order.shipping_date = timezone.now().date()
        sales_order.save()
        
        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        sales_order = self.get_object()
        
        if sales_order.status not in ['PROCESSING', 'PICKING']:
            return Response({'error': 'Order must be in processing or picking status'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Process fulfilled items
        items = SalesOrderItem.objects.filter(sales_order=sales_order)
        warehouse = sales_order.warehouse
        
        for item in items:
            inventory = Inventory.objects.get(
                product=item.product,
                warehouse=warehouse
            )
            
            if inventory.quantity < item.quantity:
                return Response({
                    'error': f'Insufficient inventory for {item.product.name}',
                    'available': inventory.quantity,
                    'required': item.quantity
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update inventory
            inventory.quantity -= item.quantity
            inventory.save()
            
            # Create inventory movement record
            InventoryMovement.objects.create(
                inventory=inventory,
                movement_type='OUT',
                quantity=item.quantity,
                reference=f"SO #{sales_order.order_number}",
                notes=f"Fulfilled for SO #{sales_order.order_number}",
                created_by=request.user
            )
        
        sales_order.status = 'PACKED'
        sales_order.save()
        
        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

class SalesOrderItemViewSet(viewsets.ModelViewSet):
    queryset = SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        sales_order = instance.sales_order
        if sales_order.status not in ['DRAFT', 'SUBMITTED']:
            raise serializers.ValidationError("Cannot delete item from sales order in current status")
        instance.delete()
        sales_order.update_totals()



