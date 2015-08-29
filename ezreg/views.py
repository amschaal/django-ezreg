from django.shortcuts import render, redirect
from django.template.context import RequestContext
from ezreg.models import Event, Price
from guardian.shortcuts import get_objects_for_user
from ezreg.forms import EventForm, PriceFormsetHelper, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView

def home(request):
    return render(request, 'ezreg/home.html', {},context_instance=RequestContext(request))

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




class RegistrationWizard(SessionWizardView):
    template_name="ezreg/register.html"
    def done(self, form_list, **kwargs):
#         do_something_with_the_form_data(form_list)
        registration = RegistrationForm(form_list[0]).save()
        registration.price = form_list[1].cleaned_data['price']
        registration.save()
        print registration
        
        for form in form_list:
            print form.cleaned_data
        print form_list[1].cleaned_data['price'].amount
        return HttpResponseRedirect('/page-to-redirect-to-when-done/')
    def get_form_kwargs(self, step):
        event = Event.objects.get(Q(id=self.kwargs['slug_or_id'])|Q(slug=self.kwargs['slug_or_id']))
        print self.kwargs
#         if str(step) == '1':
#             return {'event':event}
        return {'event':event}