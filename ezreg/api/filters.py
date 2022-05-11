from rest_framework import filters
import operator
from functools import reduce
from django.db.models.query_utils import Q

class MultiFilter(filters.BaseFilterBackend):
    """
    filter by status name or 'none' to see null status
    """
    def filter_queryset(self, request, queryset, view):
        multi_filters = getattr(view, 'multi_filters',[])
        filters = {}
        for mf in multi_filters:
            val = view.request.query_params.getlist(mf,None)
            if val:
                filters[mf]=val
        if len(filters):
            queryset = queryset.filter(**filters)
        return queryset

class OrFilter(filters.BaseFilterBackend):
    #in view, add property like:
    #or_filters = {'registrant':['registration__first_name__icontains', 'registration__last_name__icontains', 'registration__email__icontains']}
    def filter_queryset(self, request, queryset, view):
        or_filters = getattr(view, 'or_filters',[])
        filters = {}
        for k, f in or_filters.items():
            val = view.request.query_params.get(k,None)
            if val:
                list_of_Q = [Q(**{key: val}) for key in f]
                queryset = queryset.filter(reduce(operator.or_, list_of_Q))
#                 filters[k]=val
        return queryset