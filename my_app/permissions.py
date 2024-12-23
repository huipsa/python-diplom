from rest_framework.permissions import BasePermission


class IsNotAuth(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsShopOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.type == 'shop'
