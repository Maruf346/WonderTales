from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        # Handle cases where the object is a User itself or has a 'user' attribute
        owner = getattr(obj, 'user', None)
        if owner is None and isinstance(obj, permissions.get_user_model()):
            owner = obj
            
        return owner == request.user