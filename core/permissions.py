from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` or `doctor.user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user_obj = getattr(obj, 'user', None)
        if user_obj is None and hasattr(obj, 'doctor'):
            user_obj = getattr(obj.doctor, 'user', None)
        return user_obj == request.user or request.user.is_staff


class IsDoctorUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user_type == 'doctor'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'doctor' or request.user.is_staff)
        )


class IsRegularUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user_type == 'regular'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'regular' or request.user.is_staff)
        )


class IsBloodDonorUser(permissions.BasePermission):
    """
    Allows access only to authenticated users who are blood donors.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'blood_donor' or request.user.is_blood_donor or request.user.is_staff)
        )


class IsAmbulanceUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user_type == 'ambulance'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'ambulance' or request.user.is_staff)
        )


class IsPharmacyUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user_type == 'pharmacy'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'pharmacy' or request.user.is_staff)
        )


class IsDiagnosticUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user_type == 'diagnostic'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.user_type == 'diagnostic' or request.user.is_staff)
        )


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin / superuser / staff accounts.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.user_type == 'admin')
        )
