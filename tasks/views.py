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
from .models import Task, Status, TaskRelation
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


@login_required()
def task_by_code(request, code):
    try:
        task = Task.objects.get(code=code)
    except ObjectDoesNotExist:
        print("Task with such code doesn't exist")
        return HttpResponseRedirect(reverse('tasks:tasks'))
    except MultipleObjectsReturned:
        print("More than one task exists with such code")
        return HttpResponseRedirect(reverse('tasks:tasks'))
    return HttpResponseRedirect(reverse('tasks:task', args=(task.id,)))


class TaskDetailView(DetailView):
    model = Task
    #template_name = 'tasks/task.html'
    template_name = 'tasks/'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        task = Task.objects.get(pk=self.object.pk)
        user = self.request.user
        # проверяем, есть ли связанные задачи:
        try:
            relation = TaskRelation.objects.get(dependant_task=task)
            linked_task = relation.linked_task
            context['linked_task'] = linked_task
            try:
                status = Status.objects.get(task=linked_task, user=user)
                if status.state == 'FINISHED':
                    context['linked_task_finished'] = True
            except ObjectDoesNotExist:
                print("There is no status for the linked task and current user, task wasn't executed by him/her")
            print("Linked task code:" + linked_task.code)
        except ObjectDoesNotExist:
            print("No linked relations for task")
        # проверяем, есть ли зависимые задачи:
        try:
            relation = TaskRelation.objects.get(linked_task=task)
            dependant_task = relation.dependant_task
            context['dependant_task'] = dependant_task
            print("Dependant task code:" + dependant_task.code)
        except ObjectDoesNotExist:
            print("No dependant relations for task")
        self.template_name = self.template_name + task.code + ".html"
        print("Template name:" + self.template_name)
        context['task'] = task
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