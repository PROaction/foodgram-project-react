from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            obj.author == request.user or request.user.is_staff
        )


# class IsOwnerOrAdmin(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         return obj.author == request.user or request.user.is_staff
