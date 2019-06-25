from django.shortcuts import render

def handler403(request):
    response = render(request,'errors/403.html', {})
    response.status_code = 403
    return response
