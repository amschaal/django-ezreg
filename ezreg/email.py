from django.template.loader import render_to_string
from django.core.mail import send_mail


def send_email(to,from_addr,subject,template,html_template=None,context={},cc=[],bcc=[]):
    html = render_to_string(html_template,context)
    body = render_to_string(template,context)
    send_mail(subject, body, from_addr,to,html_message=html,fail_silently=False)
    
def email_status(registration,from_addr,cc=[]):
    from ezreg.models import Registration
    if registration.status == Registration.STATUS_WAITLISTED:
        send_email(['amschaal@ucdavis.edu'], from_addr, 'You have been waitlisted for "%s"'%registration.event.title, 'ezreg/emails/waitlisted.txt', html_template='ezreg/emails/waitlisted.html', context={'registration':registration}, cc=cc)
    if registration.status == Registration.STATUS_WAITLIST_PENDING:
        send_email(['amschaal@ucdavis.edu'], from_addr, 'You may now register for "%s"'%registration.event.title, 'ezreg/emails/waitlist_pending.txt', html_template='ezreg/emails/waitlist_pending.html', context={'registration':registration}, cc=cc)
    if registration.status == Registration.STATUS_REGISTERED:
        send_email(['amschaal@ucdavis.edu'], from_addr, 'You are registered for "%s"'%registration.event.title, 'ezreg/emails/registered.txt', html_template='ezreg/emails/registered.html', context={'registration':registration}, cc=cc)
    if registration.status == Registration.STATUS_CANCELLED:
        send_email(['amschaal@ucdavis.edu'], from_addr, 'You registration for "%s" has been cancelled'%registration.event.title, 'ezreg/emails/cancelled.txt', html_template='ezreg/emails/cancelled.html', context={'registration':registration}, cc=cc)