from rest_framework.permissions import BasePermission

class IsFaculty(BasePermission):
    """
    Allows access only to users with the role of 'faculty'.
    """

    def has_permission(self, request, view):
        # Replace 'is_faculty' with the actual logic or field in your model
        return bool(request.user and request.user.is_authenticated and request.user.is_faculty)