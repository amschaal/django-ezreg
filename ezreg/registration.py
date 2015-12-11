from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context import RequestContext
from formtools.wizard.views import SessionWizardView

from ezreg.email import send_email, email_status
from ezreg.forms import PriceForm, ConfirmationForm, RegistrationForm
from ezreg.models import Event, Registration, Payment, EventPage
from ezreg.payment import PaymentProcessorManager
from ezreg.payment.base import BasePaymentForm
from django_json_forms.forms import JSONForm


def show_payment_form_condition(wizard):
    if wizard.registration:
        if wizard.registration.is_waitlisted or wizard.registration.is_application:
            return False
    processor = wizard.get_payment_processor()
    if processor:
        return processor.get_form()
    else:
        return False
#     return cleaned_data.get('payment_method', True) 

def show_price_form_condition(wizard):
    if wizard.registration:
        if wizard.registration.is_waitlisted or wizard.registration.is_application:
            return False
    return wizard.event.prices.count() > 0

def registration_form_custom_condition(wizard):
    if not isinstance(wizard.event.form_fields,list):
        return False
    return len(wizard.event.form_fields) > 0

class RegistrationWizard(SessionWizardView):
    form_list = [('registration_form',RegistrationForm),('registration_form_custom',RegistrationForm), ('price_form',PriceForm),('payment_form',BasePaymentForm),('confirmation_form',ConfirmationForm)] #first ConfirmationForm is ignored or replaced depending on payment method
    condition_dict={'payment_form': show_payment_form_condition,'price_form':show_price_form_condition,'registration_form_custom':registration_form_custom_condition}
    
    def done(self, form_list, **kwargs):
        registration = RegistrationForm(form_list[0].cleaned_data,instance=self.registration).save(commit=False)
        custom_data = self.get_cleaned_data_for_step('registration_form_custom') or None
        if custom_data:
            registration.data = custom_data
        if registration.status == Registration.STATUS_WAITLIST_INCOMPLETE:
            registration.status = Registration.STATUS_WAITLISTED
        elif registration.status == Registration.STATUS_APPLY_INCOMPLETE:
            registration.status = Registration.STATUS_APPLIED
#         registration.status = Registration.STATUS_WAITLISTED if self.registration.is_waitlisted else Registration.STATUS_REGISTERED 
        
        else:
            price_data = self.get_cleaned_data_for_step('price_form') or None
            if price_data:
                registration.price = price_data['price']
                payment = Payment.objects.create(registration=registration,amount=registration.price.amount,processor=price_data['payment_method'])
                payment_data = self.get_cleaned_data_for_step('payment_form') or None
                if payment_data:
                    payment.data = payment_data
                    payment.save()
                    processor = self.get_payment_processor()
                    if processor:
                        processor.post_process_form(payment, payment_data)
                if payment.get_post_form():
                    registration.save()
                    return HttpResponseRedirect(reverse('pay',kwargs={'id':registration.id}))
            else:
                registration.status = Registration.STATUS_REGISTERED
        registration.save()
        email_status(registration)
        self.storage.reset()
        return HttpResponseRedirect(reverse('registration',kwargs={'id':registration.id}))
    def get_template_names(self):
        form = self.get_form()
        if hasattr(form, 'template'):
            return form.template
        return 'ezreg/registration/register.html'
    def get_form_kwargs(self, step):
        kwargs = {'event':self.event}
        if step == 'registration_form' and self.registration:
            kwargs['instance'] = self.registration
        return kwargs
    def get_registration(self):
        if hasattr(self, 'registration_instance'):
            return self.registration_instance
        if self.kwargs.has_key('registration_id'):
            try:
                self.registration_instance = Registration.objects.get(id=self.kwargs['registration_id'],event_id=self.event.id,status__in=[Registration.STATUS_WAITLIST_PENDING,Registration.STATUS_APPLIED_ACCEPTED])
            except Registration.DoesNotExist, e:
                raise Exception("No registration was found that was eligible for completion.")
        elif self.storage.data.has_key('registration_id'):
            self.registration_instance = Registration.objects.filter(id=self.storage.data['registration_id'],event_id=self.event.id).first()
        else:
            self.registration_instance = None
        return self.registration_instance
        
        
#         if hasattr(self, 'registration_instance'):
#             return self.registration_instance
#         if self.kwargs.has_key('registration_id'):
#             try:
#                 self.registration_instance = Registration.objects.get(id=self.kwargs['registration_id'],event_id=self.event.id,status__in=[Registration.STATUS_WAITLIST_PENDING,Registration.STATUS_APPLIED_ACCEPTED])
#             except Registration.DoesNotExist, e:
#                 raise Exception("No registration was found that was eligible for completion.")
#         elif not self.storage.data.has_key('registration_id'):
#             self.registration_instance = None
#         elif not hasattr(self, 'registration_instance'):
#             try:
#                 self.registration_instance = Registration.objects.get(id=self.storage.data['registration_id'],event_id=self.event.id)
#             except Registration.DoesNotExist, e:
#                 self.registration_instance = None
#         return self.registration_instance
    @property
    def registration(self):
        if not self.get_registration():
            self.registration_instance = self.start_registration()
        return self.registration_instance
    @property
    def event(self):
        if not hasattr(self, 'event_instance'):
            self.event_instance = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
        return self.event_instance
    def start_registration(self):
        self.delete_registration() #Don't allow past registrations to hang around.
        if self.event.can_apply():
            status = Registration.STATUS_APPLY_INCOMPLETE
        elif self.event.can_register():
            status = Registration.STATUS_PENDING_INCOMPLETE
        elif self.event.can_waitlist():
            status = Registration.STATUS_WAITLIST_INCOMPLETE
        registration = Registration.objects.create(event=self.event,status=status,test=self.test)
        self.storage.data['registration_id'] = registration.id
        return registration
    def cancel_registration(self):
        self.delete_registration(force=True)
        return HttpResponseRedirect(reverse('event',kwargs={'slug_or_id':self.event.id}))
    def delete_registration(self,force=False):
        if self.get_registration():
            if self.registration.status in [Registration.STATUS_APPLY_INCOMPLETE,Registration.STATUS_PENDING_INCOMPLETE,Registration.STATUS_WAITLIST_INCOMPLETE] or force:
                self.registration_instance.delete()
            del self.registration_instance
        if self.storage.data.has_key('registration_id'):
            Registration.objects.filter(id=self.storage.data['registration_id'],status__in=[Registration.STATUS_APPLY_INCOMPLETE,Registration.STATUS_PENDING_INCOMPLETE,Registration.STATUS_WAITLIST_INCOMPLETE]).delete()
        self.storage.reset()
    def get_payment_processor(self):
        cleaned_data = self.get_cleaned_data_for_step('price_form') or None
        if not cleaned_data:
            return None
        processor_method = cleaned_data.get('payment_method')
        if not processor_method:
            return None
        manager  = PaymentProcessorManager()
        return manager.get_processor(processor_method.processor_id)
    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        context.update({'event': self.event})
        context['registration'] = self.registration
        context['registration_form'] = self.get_cleaned_data_for_step('registration_form') or None
        custom_data_fields = []
        custom_data = self.get_cleaned_data_for_step('registration_form_custom')
        if custom_data:
            for field in self.event.form_fields:
                if field.has_key('name'):
                    if custom_data.has_key(field['name']):
                        custom_data_fields.append({'name':field['name'],'label':field['label'],'value':custom_data[field['name']]})
        context['registration_form_custom'] = custom_data_fields
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
        self.test = request.GET.has_key('test')
        test_redirect_parameter = '?test' if self.test else ''
        #custom crap HERE
        if not self.registration:
            if not (self.event.can_register() or self.event.can_apply() or self.event.can_waitlist()): 
                return render(request, 'ezreg/registration/closed.html', {'event':self.event},context_instance=RequestContext(request))
            elif self.event.can_register():
                pass
            elif self.event.can_waitlist() and not kwargs.get('waitlist',False):
                return HttpResponseRedirect(reverse('waitlist',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            elif self.event.can_apply() and not kwargs.get('apply',False):
                return HttpResponseRedirect(reverse('apply',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            self.start_registration()
        else:
            if self.registration.status == Registration.STATUS_WAITLIST_INCOMPLETE and not kwargs.get('waitlist',False):
                return HttpResponseRedirect(reverse('waitlist',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            elif self.registration.status == Registration.STATUS_APPLY_INCOMPLETE and not kwargs.get('apply',False):
                return HttpResponseRedirect(reverse('apply',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            elif self.registration.status == Registration.STATUS_PENDING_INCOMPLETE and not kwargs.get('register',False):
                return HttpResponseRedirect(reverse('register',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
        # reset the current step to the first step.
        self.storage.current_step = self.steps.first
        
        return self.render(self.get_form())
    def post(self, *args, **kwargs):
        if self.request.POST.get('wizard_goto_step', None) == 'cancel':
            return self.cancel_registration()
#         self.registration = self.storage.data['registration']
        if not self.get_registration():
            return HttpResponseRedirect(reverse('event',kwargs={'slug_or_id':self.event.id}))
        return SessionWizardView.post(self, *args, **kwargs)
    def get_form(self, step=None, data=None, files=None):
        # determine the step if not given
        if step is None:
            step = self.steps.current
        form = super(RegistrationWizard, self).get_form(step, data, files)
        if step == 'registration_form_custom':
            fields = self.event.form_fields if isinstance(self.event.form_fields,list) else []
            if not data and self.registration:
                if self.registration.data:
                    data = self.registration.data
            print fields
            if data:
                form = JSONForm(data,fields=fields)
            else:
                form = JSONForm(fields=fields)
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
