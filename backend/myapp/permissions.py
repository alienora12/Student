from rest_framework import permissions

class IsHeadAdminOrUniversityAdmin(permissions.BasePermission):
    """
    Custom permission to only allow:
    1. Head admins (no university) to access any course
    2. University admins to access only their university's courses
    """
    
    def has_permission(self, request, view):
        # Allow all users to view course list (GET requests)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Must be authenticated for modification actions
        return request.user and request.user.is_authenticated
        
    def has_object_permission(self, request, view, obj):
        # Head admin can do anything
        if request.user.is_authenticated and request.user.university is None:
            return True
            
        # Check if user is admin for this university
        if hasattr(obj, 'university'):
            return (request.user.is_authenticated and 
                    request.user.university and 
                    request.user.university.id == obj.university.id)
        
        # For University model
        return (request.user.is_authenticated and 
                request.user.university and 
                request.user.university.id == obj.id)
