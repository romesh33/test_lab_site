from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import logging
import json
import simplejson
from datetime import datetime, timezone
from django.db.models import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from .models import Task, Status
from django.contrib.auth.models import User


# Create your views here.
def theme_tasks(request, theme):
    tasks_list = Task.objects.filter(task_theme=theme)
    context = {"tasks_list": tasks_list, "theme": theme}
    return render(request, 'tasks/list_of_tasks.html', context)


def tasks(request):
    tasks_list = Task.objects.all()
    context = {"tasks_list": tasks_list}
    return render(request, 'tasks/list_of_tasks.html', context)


@login_required()
def start(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    user = request.user
    try:
        status = Status.objects.get(user=user, task=task)
    except ObjectDoesNotExist:
        print('Status not found!')
    except MultipleObjectsReturned:
        print('More then one Status was found!')
    status.start_time = datetime.now(timezone.utc)
    status.state = 'RUNNING'
    status.save()
    print("Started task with id = " + task_id)
    return HttpResponseRedirect(reverse('tasks:task', args=(task_id)))


@login_required()
def stop(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    user = request.user
    try:
        status = Status.objects.get(task=task, user=user)
    except ObjectDoesNotExist:
        print('Status not found!')
    except MultipleObjectsReturned:
        print('More then one Status was found!')
    status.stop_time = datetime.now(timezone.utc)
    if status.comeback_time:
        if status.comeback_time < status.stop_time:
            status.duration = status.duration + (status.stop_time - status.comeback_time)
        else:
            status.duration = status.duration + (status.comeback_time - status.stop_time)
    else:
        status.duration = status.duration + (status.stop_time - status.start_time)
    status.state = 'STOPPED'
    status.save()
    print("Stopped task with id = " + task_id)
    return HttpResponseRedirect(reverse('tasks:task', args=(task_id,)))


@login_required()
def come_back(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    user = request.user
    try:
        status = Status.objects.get(task=task, user=user)
    except ObjectDoesNotExist:
        print('Status not found!')
    except MultipleObjectsReturned:
        print('More then one Status was found!')
    status.state = 'RUNNING'
    status.comeback_time = datetime.now(timezone.utc)
    status.save()
    print("Came back to task with id = " + task_id)
    return HttpResponseRedirect(reverse('tasks:task', args=(task_id,)))


@login_required()
def finish(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    user = request.user
    try:
        status = Status.objects.get(task=task, user=user)
    except ObjectDoesNotExist:
        print('Status not found!')
    except MultipleObjectsReturned:
        print('More then one Status was found!')
    status.state = 'FINISHED'
    status.finish_time = datetime.now(timezone.utc)
    if status.stop_time or status.comeback_time:
        # если были остановки или продолжения
        if status.stop_time and not status.comeback_time:
            # если были остановки, но не было продолжений:
            status.duration = status.stop_time - status.start_time
        elif status.stop_time and status.comeback_time:
            # если были и остановки, и продолжения:
            if status.comeback_time < status.stop_time:
                # если остановка была после продолжения (юзер нажал на стоп и после этого - на финиш):
                status.duration = status.duration + (status.finish_time - status.stop_time)
            elif status.comeback_time > status.stop_time:
                # если остановка была до продолжения (юзер нажал на продолжить и после этого - на финиш):
                status.duration = status.duration + (status.finish_time - status.comeback_time)
        else:
            # если были продолжения, но не было остановок (такого не может быть):
            print("Unbelievable!")
    else:
        # задача завершилась сразу после начала (не было остановок и продолжений)
        status.duration = status.finish_time - status.start_time
    status.save()
    print("Finished task with id = " + task_id)
    return HttpResponseRedirect(reverse('tasks:task', args=(task_id,)))


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        task = Task.objects.get(pk=self.object.pk)
        context['task'] = task
        user = self.request.user
        try:
            status = Status.objects.get(task=task,user=user)
        except ObjectDoesNotExist:
            print('Status not found!')
            status = Status(user=user, task=task, state='IDLE')
            status.save()
        except MultipleObjectsReturned:
            print('More then one Status was found!')
        if status:
            context['status'] = status
        return context