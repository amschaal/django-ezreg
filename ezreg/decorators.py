from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from ezreg.models import OrganizerUserPermission
from django.urls.base import reverse
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
            if not request.user.is_staff:
                user_perms = [p.permission for p in event.organizer.user_permissions.filter(user=request.user)]
                if self.require_all:
                    for perm in self.perms:
                        if perm not in user_perms:
                            raise PermissionDenied
                elif len(set(user_perms).intersection(self.perms))==0:
                    raise PermissionDenied
            return f(*args,**kwargs)
        return wrapped_f

class generic_permission_decorator(object):

    def __init__(self, perms, reverse_filter, filter_param, require_all=True):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
#         print "Inside __init__()"
        self.perms = perms
#         self.model = model
        self.reverse_filter = reverse_filter
        self.filter_param  = filter_param
        self.require_all = require_all
    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
#         print "Inside __call__()"
        def wrapped_f(*args,**kwargs):
            request = args[0]
            
            if not request.user.is_authenticated():
                if not request.is_ajax():
#                     @todo: use correct url
                    url = reverse('home') + '?next=%s' % request.get_full_path()
                    return redirect(url)
                else:
                    raise PermissionDenied
            if not request.user.is_staff:
                oup_kwargs = {'user':request.user,self.reverse_filter:kwargs[self.filter_param]}
                user_perms = [p.permission for p in OrganizerUserPermission.objects.filter(**oup_kwargs)]
                if self.require_all:
                    for perm in self.perms:
                        if perm not in user_perms:
                            raise PermissionDenied
                elif len(set(user_perms).intersection(self.perms))==0:
                    raise PermissionDenied
            return f(*args,**kwargs)
        return wrapped_f

class has_permissions(object):

    def __init__(self, perms, require_all=True):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.perms = perms
        self.require_all = require_all
    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
#         print "Inside __call__()"
        def wrapped_f(*args,**kwargs):
            request = args[0]
            if not request.user.is_authenticated():
                if not request.is_ajax():
                    url = reverse('home') + '?next=%s' % request.get_full_path()
                    return redirect(url)
                else:
                    raise PermissionDenied
            if not request.user.is_staff:
                user_perms = [p.permission for p in OrganizerUserPermission.objects.filter(user=request.user)]
                if self.require_all:
                    for perm in self.perms:
                        if perm not in user_perms:
                            raise PermissionDenied
                elif len(set(user_perms).intersection(self.perms))==0:
                    raise PermissionDenied
            return f(*args,**kwargs)
        return wrapped_f