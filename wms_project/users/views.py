from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile, Activity
from .serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    UserProfileCreateSerializer,
    ActivitySerializer
)
from .permissions import IsAdminOrManager, IsSelfOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'role', 'phone']
    ordering_fields = ['user__username', 'role', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserProfileCreateSerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = UserProfile.objects.all()
        
        # Filter by warehouse if specified
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(warehouses__id=warehouse_id)
        
        # Filter by role if specified
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
            
        # Admin and managers can see all users
        if user.profile.role in ['ADMIN', 'MANAGER']:
            return queryset
        
        # Supervisors can see users in their warehouses
        if user.profile.role == 'SUPERVISOR':
            return queryset.filter(
                Q(warehouses__in=user.profile.warehouses.all()) | 
                Q(pk=user.profile.pk)
            ).distinct()
            
        # Others can only see themselves
        return queryset.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'action', 'description', 'model_name']
    ordering_fields = ['timestamp', 'action']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Activity.objects.all()
        
        # Admin can see all activities
        if user.profile.role == 'ADMIN':
            return queryset
            
        # Managers can see activities related to their warehouses
        if user.profile.role == 'MANAGER':
            warehouse_users = UserProfile.objects.filter(
                warehouses__in=user.profile.warehouses.all()
            ).values_list('user', flat=True)
            return queryset.filter(
                Q(user__in=warehouse_users) | 
                Q(user=user)
            ).distinct()
            
        # Others can only see their own activities
        return queryset.filter(user=user)