from rest_framework import permissions
from django.db.models import Q

class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admins and managers to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in ['ADMIN', 'MANAGER']

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a report to edit it.
    Admins can edit any report.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            if request.user.profile.role == 'ADMIN':
                return True
            if request.user.profile.role == 'MANAGER':
                # Managers can view reports for their warehouses
                user_warehouses = request.user.profile.warehouses.all()
                obj_warehouses = obj.warehouses.all()
                return (
                    any(w in user_warehouses for w in obj_warehouses) or 
                    obj.created_by == request.user or
                    obj.is_public
                )
            return obj.created_by == request.user or obj.is_public
        
        # Write permissions
        return request.user.profile.role == 'ADMIN' or obj.created_by == request.user