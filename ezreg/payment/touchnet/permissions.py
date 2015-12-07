from rest_framework import permissions
from django.conf import settings
class IPAddressPermission(permissions.BasePermission):
    """
    In order to whitelist IP addresses, set TOUCHNET_IP_WHITELIST
    IE: TOUCHNET_IP_WHITELIST = ['123.456.123.456','987.654'] # Accept exact addresses, or any address that starts with the included addresses
    You may just want to just use your webserver to restrict access to the postback url instead.
    Also, using the posting_key parameter is the highly recommended.
    """
    def has_permission(self, request, view):
        if not hasattr(settings, 'TOUCHNET_IP_WHITELIST'):
            return True
        ip_addr = request.META['REMOTE_ADDR']
        for ip in settings.TOUCHNET_IP_WHITELIST:
            if ip_addr.startswith(ip):
                return True
        return False
