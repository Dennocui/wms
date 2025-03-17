from rest_framework import permissions

class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admins and managers to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in ['ADMIN', 'MANAGER']

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profiles.
    Admins can edit any profile.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            if request.user.profile.role in ['ADMIN', 'MANAGER']:
                return True
            if request.user.profile.role == 'SUPERVISOR':
                # Supervisors can view users in their warehouses
                user_warehouses = request.user.profile.warehouses.all()
                obj_warehouses = obj.warehouses.all()
                return any(w in user_warehouses for w in obj_warehouses) or obj.user == request.user
            return obj.user == request.user
        
        # Write permissions
        return request.user.profile.role == 'ADMIN' or obj.user == request.user