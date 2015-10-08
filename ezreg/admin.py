from django.contrib import admin
from ezreg.models import Organizer, OrganizerUserPermission

class OrganizerAdmin(admin.ModelAdmin):
    pass
class OrganizerUserPermissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(OrganizerUserPermission, OrganizerUserPermissionAdmin)

