from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context import RequestContext
from formtools.wizard.views import SessionWizardView

from ezreg.forms import PriceForm, ConfirmationForm, RegistrationForm
from ezreg.models import Event, Registration, Payment, EventPage
from ezreg.payment import PaymentProcessorManager
from ezreg.payment.base import BasePaymentForm
from ezreg.email import send_email


def show_payment_form_condition(wizard):
    if wizard.registration:
        if wizard.registration.is_waitlisted:
            return False
    cleaned_data = wizard.get_cleaned_data_for_step('price_form') or None
    if not cleaned_data:
        return False
    processor_method = cleaned_data.get('payment_method')
    if not processor_method:
        return False
    manager  = PaymentProcessorManager()
    processor = manager.get_processor(processor_method.processor_id)
    return processor.get_form()
#     return cleaned_data.get('payment_method', True)

def show_price_form_condition(wizard):
    if wizard.registration:
        if wizard.registration.is_waitlisted:
            return False
    return wizard.event.prices.count() > 0
    

class RegistrationWizard(SessionWizardView):
    form_list = [('registration_form',RegistrationForm), ('price_form',PriceForm),('payment_form',BasePaymentForm),('confirmation_form',ConfirmationForm)] #first ConfirmationForm is ignored or replaced depending on payment method
    condition_dict={'payment_form': show_payment_form_condition,'price_form':show_price_form_condition}
    def done(self, form_list, **kwargs):
        registration = RegistrationForm(form_list[0].cleaned_data,instance=self.registration).save(commit=False)
        registration.status = Registration.STATUS_WAITLISTED if self.registration.is_waitlisted else Registration.STATUS_REGISTERED 
        registration.save()
        
        price_data = self.get_cleaned_data_for_step('price_form') or None
        if price_data:
            registration.price = price_data['price']
            registration.save()
            payment = Payment.objects.create(registration=registration,amount=registration.price.amount,processor=price_data['payment_method'])
            payment_data = self.get_cleaned_data_for_step('payment_form') or None
            if payment_data:
                payment.data = payment_data
                payment.save()
            if payment.get_post_form():
                return HttpResponseRedirect(reverse('pay',kwargs={'id':registration.id}))
        if registration.is_waitlisted:
            send_email(['amschaal@ucdavis.edu'], 'no-reply@genomecenter.ucdavis.edu', 'You have been waitlisted for "%s"'%self.event.title, 'ezreg/emails/waitlisted.txt', html_template='ezreg/emails/waitlisted.html', context={'registration':registration}, cc=[])#registration.email
        return HttpResponseRedirect(reverse('registration',kwargs={'id':registration.id}))
    def get_template_names(self):
        form = self.get_form()
        if hasattr(form, 'template'):
            return form.template
        return 'ezreg/register.html'
    def get_form_kwargs(self, step):
        return {'event':self.event}
    @property
    def registration(self):
        if not self.storage.data.has_key('registration_id'):
            return None
        if not hasattr(self, 'registration_instance'):
            try:
                self.registration_instance = Registration.objects.get(id=self.storage.data['registration_id'])
            except Registration.DoesNotExist, e:
                self.registration_instance = self.start_registration()
        return self.registration_instance
    @property
    def event(self):
        if not hasattr(self, 'event_instance'):
            self.event_instance = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
        return self.event_instance
    def start_registration(self):
        self.storage.reset()
        if self.event.registration_open:
            status = Registration.STATUS_PENDING_INCOMPLETE
        else:
            status = Registration.STATUS_WAITLIST_PENDING
        registration = Registration.objects.create(event=self.event,status=status)
        self.storage.data['registration_id'] = registration.id
        return registration
    def cancel_registration(self):
        if self.registration:
            self.registration.delete()
        self.storage.reset()
        return HttpResponseRedirect(reverse('event',kwargs={'slug_or_id':self.event.id}))
    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        context.update({'event': self.event})
        context['registration'] = self.registration
        context['registration_form'] = self.get_cleaned_data_for_step('registration_form') or None
        context['price'] = self.get_cleaned_data_for_step('price_form') or None
        context['payment'] = self.get_cleaned_data_for_step('payment_form') or None
        return context
#     def dispatch(self, request, *args, **kwargs):
#         self.event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
#         return SessionWizardView.dispatch(self, request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        """
        This method handles GET requests.

        If a GET request reaches this point, the wizard assumes that the user
        just starts at the first step or wants to restart the process.
        The data of the wizard will be resetted before rendering the first step
        """
        #custom crap HERE
        if not self.registration:
            if not self.event.registration_open:
                if self.event.waitlist_open:
                    if not kwargs['waitlist']:
                        return HttpResponseRedirect(reverse('waitlist',kwargs={'slug_or_id':self.event.slug_or_id}))
                else:
                    return render(request, 'ezreg/registration/closed.html', {'event':self.event},context_instance=RequestContext(request))
            self.start_registration()
        else:
            if self.registration.status == Registration.STATUS_WAITLIST_PENDING and not kwargs['waitlist']:
                return HttpResponseRedirect(reverse('waitlist',kwargs={'slug_or_id':self.event.slug_or_id}))
        # reset the current step to the first step.
        self.storage.current_step = self.steps.first
        
        return self.render(self.get_form())
    def post(self, *args, **kwargs):
        if self.request.POST.get('wizard_goto_step', None) == 'cancel':
            return self.cancel_registration()
#         self.registration = self.storage.data['registration']
        return SessionWizardView.post(self, *args, **kwargs)
    def get_form(self, step=None, data=None, files=None):
        # determine the step if not given
        if step is None:
            step = self.steps.current
        form = super(RegistrationWizard, self).get_form(step, data, files)
        if step == 'payment_form':
            cleaned_data = self.get_cleaned_data_for_step('price_form') or None
            if cleaned_data:
                processor_method = cleaned_data.get('payment_method')
                manager  = PaymentProcessorManager()
                processor = manager.get_processor(processor_method.processor_id)
                form_class = processor.get_form()
                if form_class:
                    form = form_class(data,event=self.event)
        return form
