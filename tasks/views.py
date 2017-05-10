from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import logging
import json
import simplejson

from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from .models import Task
from django.contrib.auth.models import User


# Create your views here.
def tasks(request):
    tasks_list = Task.objects.all()
    context = {"tasks_list": tasks_list}
    return render(request, 'tasks/list_of_tasks.html', context)


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task.html'