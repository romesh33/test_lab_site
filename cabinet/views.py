from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
# Create your views here.
import logging
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from test_lab_site.forms import UserProfileForm
from test_lab_site.models import UserProfile
from .forms import UserCabinetForm
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
@login_required()
def viewCabinet(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    try:
        userProfile = user.userprofile
    except (ObjectDoesNotExist):
        userProfile = 0
        logging.error('ObjectDoesNotExist: There is no UserProfile for this user')
    context = {"user": user, "userprofile": userProfile,}
    return render(request, 'cabinet/cabinet_main.html', context)

@login_required()
def editProfile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # this variable is needed to hide unique username error which is shown in most cases when user edits
    #   his/her profile:
    show_unique_username_error = False
    try:
        userProfile = user.userprofile
    except (ObjectDoesNotExist):
        userProfile = UserProfile()
        userProfile.user = user
        userProfile.save()
        logging.error('UserProfile was absent for this user and it was created')
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserCabinetForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        username_from_post = request.POST['username']
        email_from_post = request.POST['email']

        if user_form.has_error('username', "unique") and not user_form.has_error('email'):
            logging.warning("username from username field = {0}, username from request = {1}"
                            .format(username_from_post, request.user.username))
            if username_from_post == request.user.username:
                # in case username is the same as from request - user wants to change e-mail (or/and other details)
                #   - in this case we are saving details for this user (except username):
                user.email = email_from_post
                user.save()
                # Now sort out the userProfile.
                #  Did the user provide a profile picture?
                #  If so, we need to get it from the input form and put it in the UserProfile model.
                if 'picture' in request.FILES:
                    userProfile.picture = request.FILES['picture']
                    userProfile.save()
                else:
                    logging.warning("picture wasn't found in request")
                return HttpResponseRedirect(reverse('cabinet:view_cabinet',args=(user.id,)))
            else:
                # in case username specified in the POST data - is not the same as logged in user -
                #   we will render the form with validation error:
                show_unique_username_error = True
                logging.warning("User tried to change the username, but it already exists")
        else:
            if user_form.is_valid() and profile_form.is_valid():
                user.username = username_from_post
                user.email = email_from_post
                user.save()
                if 'picture' in request.FILES:
                    userProfile.picture = request.FILES['picture']
                    userProfile.save()
                else:
                    logging.warning("picture wasn't found in request")
                return HttpResponseRedirect(reverse('cabinet:view_cabinet',args=(user.id,)))
            else:
                print(user_form.errors, profile_form.errors)
    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        # NEED TO INSERT Model data in forms:
        data = {
            "username": user.username,
            "email": user.email,
        }
        if userProfile.picture:
            data["picture"] = userProfile.picture
        user_form = UserCabinetForm(data)
        profile_form = UserProfileForm(data)
    context = {"user_form": user_form, "profile_form": profile_form, "show_unique_username_error":
        show_unique_username_error}
    logging.warning(show_unique_username_error)
    return render(request, 'cabinet/cabinet_edit.html', context)