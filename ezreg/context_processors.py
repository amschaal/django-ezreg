from ezreg.models import OrganizerUserPermission
from django.conf import settings

def permissions_processor(request):
    if not request.user.is_authenticated:
        return {'OrganizerUserPermission':OrganizerUserPermission}
    elif request.user.is_staff:
        permissions = [p[0] for p in OrganizerUserPermission.PERMISSION_CHOICES]
    else:
        oups = OrganizerUserPermission.objects.filter(user=request.user)
        permissions = list(set([p.permission for p in oups]))
    return {'all_user_permissions': permissions,'OrganizerUserPermission':OrganizerUserPermission}

def settings_processor(request):
    return {'HEADER_TEXT': settings.HEADER_TEXT, 'MESSAGES': settings.MESSAGES}