from rest_framework import permissions
from ezreg.models import OrganizerUserPermission

class EventPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        permission_required = OrganizerUserPermission.PERMISSION_VIEW if request.method in permissions.SAFE_METHODS else OrganizerUserPermission.PERMISSION_ADMIN
        return OrganizerUserPermission.objects.filter(organizer=obj.organizer,user=request.user,permission=permission_required).count() != 0