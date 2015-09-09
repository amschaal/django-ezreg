from django.template.loader import render_to_string
from django.core.mail import send_mail


def send_email(to,from_addr,subject,template,html_template=None,context={},cc=[],bcc=[]):
    html = render_to_string(html_template,context)
    body = render_to_string(template,context)
    send_mail(subject, body, from_addr,to,html_message=body,fail_silently=False)
    
