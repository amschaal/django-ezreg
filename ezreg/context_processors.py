from ezreg.models import OrganizerUserPermission

def permissions_processor(request):
    if not request.user.is_authenticated():
        return {'OrganizerUserPermission':OrganizerUserPermission}
    elif request.user.is_superuser:
        permissions = [p[0] for p in OrganizerUserPermission.PERMISSION_CHOICES]
    else:
        oups = OrganizerUserPermission.objects.filter(user=request.user)
        permissions = list(set([p.permission for p in oups]))
    return {'all_user_permissions': permissions,'OrganizerUserPermission':OrganizerUserPermission}
