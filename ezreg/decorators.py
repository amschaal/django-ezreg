from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
class event_access_decorator(object):

    def __init__(self, perms,event_param='event',require_all=True):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
#         print "Inside __init__()"
        self.perms = perms
        self.event_param  = event_param
        self.require_all = require_all
    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
#         print "Inside __call__()"
        def wrapped_f(*args,**kwargs):
            from ezreg.models import Event
            event = Event.objects.get(id=kwargs[self.event_param])
            kwargs[self.event_param]=event
            request = args[0]
            if not request.user.is_authenticated():
                if not request.is_ajax():
#                     @todo: use correct url
                    url = reverse('home') + '?next=%s' % request.get_full_path()
                    return redirect(url)
                else:
                    raise PermissionDenied
            if True:#not request.user.is_superuser:
                user_perms = [p.permission for p in event.organizer.user_permissions.filter(user=request.user)]
                if self.require_all:
                    for perm in self.perms:
                        if perm not in user_perms:
                            raise PermissionDenied
                elif len(set(user_perms).intersection(self.perms))==0:
                    raise PermissionDenied
            return f(*args,**kwargs)
        return wrapped_f