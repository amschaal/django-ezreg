from django.shortcuts import render, redirect
from django.template.context import RequestContext
from ezreg.models import Event, Price, Registration, PaymentProcessor, Payment
from guardian.shortcuts import get_objects_for_user
from ezreg.forms import EventForm, PriceFormsetHelper, RegistrationForm,\
    PaymentProcessorForm, PriceForm, ConfirmationForm
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse
from ezreg.payment import PaymentProcessorManager
from ezreg.payment.base import BasePaymentForm

def home(request):
    return render(request, 'ezreg/home.html', {},context_instance=RequestContext(request))

@login_required
def events(request):
    events = get_objects_for_user(request.user,'view_event',klass=Event)
    return render(request, 'ezreg/events.html', {'events':events},context_instance=RequestContext(request))

@login_required
def create_modify_event(request,id=None):
    instance = None if not id else Event.objects.get(id=id)
#     PriceFormset = formset_factory(PriceForm,extra=4,max_num=10)
#     if instance:
#         PriceFormset = modelformset_factory(Price,exclude=('event',),extra=5)
#     else:
#         PriceFormset = modelformset_factory(Price,exclude=('event',),extra=5)
    
    if request.method == 'GET':
        form = EventForm(request.user,instance=instance)
#         price_formset = PriceFormset(queryset=Price.objects.filter(event=instance))
    elif request.method == 'POST':
        form = EventForm(request.user,request.POST,instance=instance)
#         price_formset = PriceFormset(request.POST)
        if form.is_valid():
            event = form.save()
#             prices = price_formset.save(commit=False)
#             for price in prices:
#                 price.event = event
#                 price.save()
            return redirect('events') #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_event.html', {'form':form,'event':instance} ,context_instance=RequestContext(request))

def event(request,slug_or_id):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    return render(request, 'ezreg/event.html', {'event':event},context_instance=RequestContext(request))

@login_required
def registrations(request,slug_or_id):
    event = Event.objects.get(Q(id=slug_or_id)|Q(slug=slug_or_id))
    return render(request, 'ezreg/registrations.html', {'event':event},context_instance=RequestContext(request))
# def register(request,id=None):
#     instance = None if not id else Event.objects.get(id=id)
#     if request.method == 'GET':
#         form = EventForm(request.user,instance=instance)
#     elif request.method == 'POST':
#         form = EventForm(request.user,request.POST,instance=instance)
#         if form.is_valid():
#             event = form.save()
#             return redirect('events') #event.get_absolute_url()
#     return render(request, 'ezreg/create_modify_event.html', {'form':form} ,context_instance=RequestContext(request))

def registration(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/registration.html', {'registration':registration},context_instance=RequestContext(request))

def pay(request,id):
    registration = Registration.objects.get(id=id)
    return render(request, 'ezreg/pay.html', {'registration':registration},context_instance=RequestContext(request))


def show_payment_form_condition(wizard):
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
    return wizard.event.prices.count() > 0
    

class RegistrationWizard(SessionWizardView):
    form_list = [('registration_form',RegistrationForm), ('price_form',PriceForm),('payment_form',BasePaymentForm),('confirmation_form',ConfirmationForm)] #first ConfirmationForm is ignored or replaced depending on payment method
    condition_dict={'payment_form': show_payment_form_condition,'price_form':show_price_form_condition}
    def done(self, form_list, **kwargs):
        registration = RegistrationForm(form_list[0].cleaned_data).save(commit=False)
        registration.event = self.event
        registration.price = form_list[1].cleaned_data['price']
        registration.save()
        
        price_data = self.get_cleaned_data_for_step('price_form') or None
        if price_data:
            payment = Payment.objects.create(registration=registration,amount=registration.price.amount,processor=form_list[1].cleaned_data['payment_method'])
            payment_data = self.get_cleaned_data_for_step('payment_form') or None
            if payment_data:
                payment.data = payment_data
                payment.save()
            if payment.get_post_form():
                return HttpResponseRedirect(reverse('pay',kwargs={'id':registration.id}))
        
        return HttpResponseRedirect(reverse('registration',kwargs={'id':registration.id}))
    def get_template_names(self):
        form = self.get_form()
        if hasattr(form, 'template'):
            return form.template
        return 'ezreg/register.html'
    def get_form_kwargs(self, step):
        return {'event':self.event}
    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        context.update({'event': self.event})
        context['registration'] = self.get_cleaned_data_for_step('registration_form') or None
        context['price'] = self.get_cleaned_data_for_step('price_form') or None
        context['payment'] = self.get_cleaned_data_for_step('payment_form') or None
        return context
    def dispatch(self, request, *args, **kwargs):
        self.event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
        return SessionWizardView.dispatch(self, request, *args, **kwargs)
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

@login_required
def payment_processors(request):
    payment_processors = PaymentProcessor.objects.filter(group__in=request.user.groups.all())
    return render(request, 'ezreg/payment_processors.html', {'payment_processors':payment_processors},context_instance=RequestContext(request))




@login_required
def create_modify_payment_processor(request,id=None):
    instance = None if not id else PaymentProcessor.objects.get(id=id)
    if request.method == 'GET':
        form = PaymentProcessorForm(request.user,instance=instance)
    elif request.method == 'POST':
        form = PaymentProcessorForm(request.user,request.POST,instance=instance)
        if form.is_valid():
            processor = form.save()
            return redirect('payment_processors') #event.get_absolute_url()
    return render(request, 'ezreg/create_modify_payment_processor.html', {'form':form} ,context_instance=RequestContext(request))

@login_required
def configure_payment_processor(request,id):
    processor = PaymentProcessor.objects.get(id=id)
    ConfigForm = processor.get_configuration_form()
    if request.method == 'GET':
        form = ConfigForm(initial=processor.config)
    elif request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            processor.config = form.cleaned_data
            processor.save()
            return redirect('payment_processors') #event.get_absolute_url()
    return render(request, 'ezreg/configure_payment_processor.html', {'form':form,'processor':processor} ,context_instance=RequestContext(request))