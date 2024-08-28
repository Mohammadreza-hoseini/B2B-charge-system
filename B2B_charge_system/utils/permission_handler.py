from rest_framework.permissions import BasePermission


class CustomerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'customer':
            return request.user and request.user.is_authenticated


class VendorPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'vendor':
            return request.user and request.user.is_authenticated
