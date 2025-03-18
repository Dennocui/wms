
# wms_project/warehouse/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Warehouse, Zone, Location
from .serializers import WarehouseSerializer, ZoneSerializer, LocationSerializer
from inventory.models import Inventory
from inventory.serializers import InventorySerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'state', 'country']
    
    @action(detail=True, methods=['get'])
    def zones(self, request, pk=None):
        warehouse = self.get_object()
        zones = Zone.objects.filter(warehouse=warehouse)
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        warehouse = self.get_object()
        locations = Location.objects.filter(warehouse=warehouse)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        warehouse = self.get_object()
        inventory = Inventory.objects.filter(warehouse=warehouse)
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'warehouse__name']
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        zone = self.get_object()
        locations = Location.objects.filter(zone=zone)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'warehouse__name', 'zone__name', 'aisle', 'rack', 'shelf', 'bin']