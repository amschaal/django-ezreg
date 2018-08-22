from rest_framework import filters
import operator

class MultiFilter(filters.BaseFilterBackend):
    """
    filter by status name or 'none' to see null status
    """
    def filter_queryset(self, request, queryset, view):
        multi_filters = getattr(view, 'multi_filters',[])
        filters = {}
        for mf in multi_filters:
            val = view.request.query_params.getlist(mf,None)
            print mf
            print val
            if val:
                filters[mf]=val
        if len(filters):
            queryset = queryset.filter(**filters)
        return queryset