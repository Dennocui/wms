from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Category, Product, Inventory, InventoryMovement
from .serializers import (CategorySerializer, ProductSerializer, 
                         InventorySerializer, InventoryMovementSerializer)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'sku', 'barcode', 'category__name']
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        product = self.get_object()
        inventories = Inventory.objects.filter(product=product)
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'warehouse__name']
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        inventory = self.get_object()
        movements = InventoryMovement.objects.filter(inventory=inventory).order_by('-created_at')
        serializer = InventoryMovementSerializer(movements, many=True)
        return Response(serializer.data)

            
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        inventory = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        notes = request.data.get('notes', '')
        reference = request.data.get('reference', '')
        
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=400)
        
        # Update inventory
        inventory.quantity += quantity
        inventory.last_restock_date = timezone.now()
        inventory.save()
        
        # Create movement record
        movement = InventoryMovement.objects.create(
            inventory=inventory,
            movement_type='IN',
            quantity=quantity,
            reference=reference,
            notes=notes,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'new_quantity': inventory.quantity,
            'movement_id': movement.id
        })
    
    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        inventory = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        notes = request.data.get('notes', '')
        reference = request.data.get('reference', '')
        
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=400)
        
        if inventory.quantity < quantity:
            return Response({'error': 'Insufficient inventory'}, status=400)
        
        # Update inventory
        inventory.quantity -= quantity
        inventory.save()
        
        # Create movement record
        movement = InventoryMovement.objects.create(
            inventory=inventory,
            movement_type='OUT',
            quantity=quantity,
            reference=reference,
            notes=notes,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'new_quantity': inventory.quantity,
            'movement_id': movement.id
        })

class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all().order_by('-created_at')
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['inventory__product__name', 'inventory__warehouse__name', 'reference', 'notes']


