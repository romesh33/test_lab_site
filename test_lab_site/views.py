from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.template import RequestContext
from django.urls import reverse

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .forms import UserForm
from tasks.models import Task, Status, Theme

import logging

def main(request):
    # next_events_list = Event.objects.order_by('-start_time')
    # if request.user.is_authenticated():
    #     # I'll prepare the list of events in which user participates if user is logged in:
    #     user = request.user
    #     registered_event_list = Event.objects.filter(users=user)
    # else:
    #     # Do something for anonymous users.
    #     registered_event_list = 0
    #     pass
    # context = {"next_events_list": next_events_list, "registered_event_list": registered_event_list}
    #statuses = Status.objects.filter(state='FINISHED')
    #context = {'finished_tasks_counter': statuses.count()}
    context = {}
    return render(request, 'main.html', context)


def about(request):
    return render(request, 'about.html', {})


def stats(request):
    return render(request, 'stats.html', {})


def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information..
        user_form = UserForm(data=request.POST)

        # If form is valid
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            # Update our variable to tell the template registration was successful.
            registered = True
        # Invalid form - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
    # Render the template depending on the context.
    return render(request,
                  'register.html',
                  {'user_form': user_form, 'registered': registered})


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        print("This is POST request")
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                print(request.POST.get('next', reverse('main')))
                if request.POST.get('next') == '' or not request.POST.get('next'):
                    return HttpResponseRedirect(reverse('main'))
                else:
                    return HttpResponseRedirect(request.POST.get('next'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            return render(request, 'login.html', {'wrong_details': True, 'next': request.GET.get('next', '')})
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', {'wrong_details': False, 'next': request.GET.get('next', '')})


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('main'))
