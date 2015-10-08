from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail.message import EmailMultiAlternatives
from icalendar import Calendar, Event, vText
from datetime import datetime
from mailqueue.models import MailerMessage
from django.core.files import File
# def send_email(to,from_addr,subject,template,html_template=None,context={},cc=[],bcc=[]):
#     html = render_to_string(html_template,context)
#     body = render_to_string(template,context)
#     send_mail(subject, body, from_addr,to,html_message=html,fail_silently=False)

def generate_email(to,from_addr,subject,template,html_template=None,context={},bcc=None,registration=None):
    
    html = render_to_string(html_template,context)
    body = render_to_string(template,context)
    message = MailerMessage(to_address=', '.join(to),from_address=from_addr,subject=subject,content=body,html_content=html)
    if bcc:
        message.bcc_address = ', '.join(bcc)
#     msg = EmailMultiAlternatives(subject, body, from_addr, to, bcc)
#     msg.attach_alternative(html, 'text/html')
    return message
    
    
def send_email(to,from_addr,subject,template,html_template=None,context={},cc=[],bcc=[],registration=None):
    msg = generate_email(to, from_addr, subject, template, html_template, context, bcc)
    msg.save()
    if registration:
        registration.email_messages.add(msg)
        registration.save()
    return msg
        
def send_ical_email(event,to,from_addr,subject,template,html_template=None,context={},cc=None,bcc=None,registration=None):
    msg = generate_email(to, from_addr, subject, template, html_template, context, bcc)
    print 'Event ical'
    print event.ical
    if event.ical:
        from django.core.files import File
        ical = File(open(event.ical, "r"))
        msg.add_attachment(ical)
    msg.save()
    if registration:
        registration.email_messages.add(msg)
        registration.save()
    return msg
def generate_event_ical(event):
    calendar = Calendar()
    cevent = Event()
    if event.start_time:
        cevent.add('dtstart', event.start_time)
        if event.end_time:
            cevent.add('dtend', event.end_time)
    if event.address:
        cevent.add('location',vText(event.address))
    cevent.add('summary', event.title)
    calendar.add_component(cevent)
    return calendar.to_ical()

def email_status(registration,from_addr,cc=[]):
    from ezreg.models import Registration
    if registration.status == Registration.STATUS_WAITLISTED:
        return send_email(['amschaal@ucdavis.edu'], from_addr, 'You have been waitlisted for "%s"'%registration.event.title, 'ezreg/emails/waitlisted.txt', html_template='ezreg/emails/waitlisted.html', context={'registration':registration}, bcc=cc, registration=registration)
    if registration.status == Registration.STATUS_WAITLIST_PENDING:
        return send_email(['amschaal@ucdavis.edu'], from_addr, 'You may now register for "%s"'%registration.event.title, 'ezreg/emails/waitlist_pending.txt', html_template='ezreg/emails/waitlist_pending.html', context={'registration':registration}, bcc=cc, registration=registration)
    if registration.status == Registration.STATUS_REGISTERED:
        return send_ical_email(registration.event,['amschaal@ucdavis.edu'], from_addr, 'You are registered for "%s"'%registration.event.title, 'ezreg/emails/registered.txt', html_template='ezreg/emails/registered.html', context={'registration':registration}, bcc=cc, registration=registration)
    if registration.status == Registration.STATUS_CANCELLED:
        return send_email(['amschaal@ucdavis.edu'], from_addr, 'You registration for "%s" has been cancelled'%registration.event.title, 'ezreg/emails/cancelled.txt', html_template='ezreg/emails/cancelled.html', context={'registration':registration}, bcc=cc, registration=registration)