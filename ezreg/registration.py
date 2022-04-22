from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context import RequestContext
from formtools.wizard.views import SessionWizardView

from ezreg.email import send_email, email_status
from ezreg.forms import PriceForm, ConfirmationForm, RegistrationForm
from ezreg.models import Event, Registration, Payment, EventPage,\
    OrganizerUserPermission
from ezreg.payment import PaymentProcessorManager
from ezreg.payment.base import BasePaymentForm
from django_json_forms.forms import JSONForm
from ezreg.exceptions import RegistrationClosedException
from django.http.response import HttpResponseForbidden
from django.utils import timezone
from django.http import Http404
from django.urls import reverse

def show_payment_form_condition(wizard):
    if wizard.registration:
        price_data = wizard.get_cleaned_data_for_step('price_form') or None
        if price_data and price_data['price'].amount == 0.0:
            return False
        if wizard.registration.is_waitlisted or wizard.registration.is_application or wizard.registration.registered_by:
            return False
    processor = wizard.get_payment_processor()
    if processor:
        return processor.get_form()
    else:
        return False
#     return cleaned_data.get('payment_method', True) 

def show_price_form_condition(wizard):
    if wizard.registration:
        if wizard.registration.is_waitlisted or wizard.registration.is_application or wizard.registration.registered_by:
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
        registration = RegistrationForm(form_list[0].cleaned_data,event=self.event,instance=self.registration).save(commit=False)
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
                if registration.price.amount > 0.0:
                    payment = Payment.objects.filter(registration=registration).first()
                    if payment:
                        payment.amount = registration.price.amount
                        payment.processor=price_data['payment_method']
                        payment.save()
                    else:
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
            else:
                registration.status = Registration.STATUS_REGISTERED
        registration.registered = timezone.now()
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
        if step == 'registration_form':
            if self.registration:
                kwargs['instance'] = self.registration
            if getattr(self, 'admin',False):
                kwargs['admin'] = True
        return kwargs
    def get_registration(self):
        if hasattr(self, 'registration_instance'):
            return self.registration_instance
        #A registration id was passed as part of the URL
        if self.kwargs.has_key('registration_id'):
            self.registration_instance = Registration.objects.get(id=self.kwargs['registration_id'],status__in=[Registration.STATUS_WAITLIST_PENDING,Registration.STATUS_APPLIED_ACCEPTED])
        elif self.get_session_registration_id():
            self.registration_instance = Registration.objects.filter(id=self.get_session_registration_id()).first()
        else:
            self.registration_instance = None
        return self.registration_instance
        
    @property
    def registration(self):
        if not self.get_registration():
            self.registration_instance = self.create_registration()
        return self.registration_instance
    @property
    def event(self):
        if not hasattr(self, 'event_instance'):
            try:
                self.event_instance = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
            except Event.DoesNotExist:
                raise Http404('Registration not found')
        return self.event_instance
    def get_session_registration_id(self):
            return self.storage.data['registration_id'] if self.storage.data.has_key('registration_id') else None
    def set_session_registration_id(self,id):
            self.storage.data['registration_id'] = id
    def create_registration(self):
        self.delete_registration() #Don't allow past registrations to hang around.
        
        if self.event.can_apply():
            status = Registration.STATUS_APPLY_INCOMPLETE
        elif self.event.can_register():
            status = Registration.STATUS_PENDING_INCOMPLETE
        elif self.event.can_waitlist():
            status = Registration.STATUS_WAITLIST_INCOMPLETE
        elif not getattr(self, 'admin',False):
            raise RegistrationClosedException("Registration is closed")
        if getattr(self,'admin', False):
            registration = Registration.objects.create(event=self.event,status=Registration.STATUS_PENDING_INCOMPLETE,test=self.test, registered_by=self.request.user)
        else:
            registration = Registration.objects.create(event=self.event,status=status,test=self.test)
        self.set_session_registration_id(registration.id)
        return registration
    def cancel_registration(self):
        registration = self.get_registration()
        if registration and registration.status in [Registration.STATUS_PENDING_INCOMPLETE, Registration.STATUS_APPLY_INCOMPLETE, Registration.STATUS_WAITLIST_INCOMPLETE]:
            self.delete_registration(force=True)
        return HttpResponseRedirect(reverse('event',kwargs={'slug_or_id':self.event.id}))
    def delete_registration(self,force=False):
        if self.get_registration():
            if self.registration.status in [Registration.STATUS_APPLY_INCOMPLETE,Registration.STATUS_PENDING_INCOMPLETE,Registration.STATUS_WAITLIST_INCOMPLETE] or force:
                self.registration_instance.delete()
            del self.registration_instance
        if self.get_session_registration_id():
            Registration.objects.filter(id=self.get_session_registration_id(),status__in=[Registration.STATUS_APPLY_INCOMPLETE,Registration.STATUS_PENDING_INCOMPLETE,Registration.STATUS_WAITLIST_INCOMPLETE]).delete()
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
            context['registration_form_custom'] = self.get_form('registration_form_custom', custom_data)
#             for field in self.event.form_fields:
#                 if field.has_key('name'):
#                     if custom_data.has_key(field['name']):
#                         custom_data_fields.append({'name':field['name'],'label':field['label'],'value':custom_data[field['name']]})
#         context['registration_form_custom'] = custom_data_fields
        context['price'] = self.get_cleaned_data_for_step('price_form') or None
        context['payment'] = self.get_cleaned_data_for_step('payment_form') or None
        if context['payment']:
            context['payment_form'] = self.get_form('payment_form', context['payment'])
        return context
#     def dispatch(self, request, *args, **kwargs):
#         self.event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
#         return SessionWizardView.dispatch(self, request, *args, **kwargs)
    #prefix is used to key session storage
    def get_prefix(self, request, *args, **kwargs):
        return self.event.id
    def get(self, request, *args, **kwargs):
        #If there is already a registration started, resume it
        self.event.delete_expired_registrations()
        try:
            existing_registration = self.get_registration()
        except Registration.DoesNotExist as e:
            return render(request, 'ezreg/registration/doesnotexist.html', {'event':self.event})
        if existing_registration:
            self.render_goto_step(self.steps.first)
        
        self.test = request.GET.has_key('test')
        if kwargs.get('admin',False):
            if not (request.user.is_authenticated and request.user.is_staff) and not OrganizerUserPermission.objects.filter(user=request.user,permission=OrganizerUserPermission.PERMISSION_ADMIN,organizer=self.event.organizer):
                return HttpResponseForbidden('Only event admininstrators may register participants')
            self.admin = True
        test_redirect_parameter = '?test' if self.test else ''
        
        try:
            registration = self.registration
            if registration.status == Registration.STATUS_WAITLIST_INCOMPLETE and not kwargs.get('waitlist',False):
                return HttpResponseRedirect(reverse('waitlist',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            elif registration.status == Registration.STATUS_APPLY_INCOMPLETE and not kwargs.get('apply',False):
                return HttpResponseRedirect(reverse('apply',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
            elif registration.status == Registration.STATUS_PENDING_INCOMPLETE and not kwargs.get('register',False):
                return HttpResponseRedirect(reverse('register',kwargs={'slug_or_id':self.event.slug_or_id})+test_redirect_parameter)
        except RegistrationClosedException:
            return render(request, 'ezreg/registration/closed.html', {'event':self.event})
        # reset the current step to the first step.
        self.storage.current_step = self.steps.first
        
        return self.render(self.get_form())
    def post(self, *args, **kwargs):
        if self.request.POST.get('wizard_goto_step', None) == 'cancel':
            return self.cancel_registration()
        self.event.delete_expired_registrations()
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
            print(fields)
            if data:
                form = JSONForm(data,fields=fields)
            else:
                form = JSONForm(fields=fields)
        if step == 'payment_form':
            cleaned_data = self.get_cleaned_data_for_step('price_form') or None
            if cleaned_data:
                processor_method = cleaned_data.get('payment_method')
                if processor_method:
                    manager  = PaymentProcessorManager()
                    processor = manager.get_processor(processor_method.processor_id)
                    form_class = processor.get_form()
                    if form_class:
                        form = form_class(data,event=self.event,config=processor_method.config)
        return form
