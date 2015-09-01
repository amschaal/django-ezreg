from django.shortcuts import render, redirect
from django.template.context import RequestContext
from ezreg.models import Event, Price, Registration, PaymentProcessor
from guardian.shortcuts import get_objects_for_user
from ezreg.forms import EventForm, PriceFormsetHelper, RegistrationForm,\
    PaymentProcessorForm
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse

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


class RegistrationWizard(SessionWizardView):
    template_name="ezreg/register.html"
    def done(self, form_list, **kwargs):
#         do_something_with_the_form_data(form_list)
        print 'done'
        print form_list[0].cleaned_data
        registration = RegistrationForm(form_list[0].cleaned_data).save(commit=False)
        registration.event = self.event
        print registration
        registration.price = form_list[1].cleaned_data['price']
        registration.save()
        print registration
        
        for form in form_list:
            print form.cleaned_data
        print form_list[1].cleaned_data['price'].amount
        
        return HttpResponseRedirect(reverse('registration',kwargs={'id':registration.id}))
    def get_form_kwargs(self, step):
#         event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
#         print self.kwargs
#         if str(step) == '1':
#             return {'event':event}
        return {'event':self.event}
    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        context.update({'event': self.event})
        return context
    def dispatch(self, request, *args, **kwargs):
        self.event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
        return SessionWizardView.dispatch(self, request, *args, **kwargs)

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