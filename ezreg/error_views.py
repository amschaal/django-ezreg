from django.shortcuts import render_to_response
from django.template import RequestContext

def handler403(request):
    response = render_to_response('errors/403.html', {},context_instance=RequestContext(request))
    response.status_code = 403
    return response
