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
from .models import Task, Status, TaskRelation, Theme
from django.contrib.auth.models import User


# Create your views here.
def theme_tasks(request, theme):
    theme = Theme.objects.get(theme_code=theme)
    tasks_list = Task.objects.filter(task_theme=theme)
    # задаем словарь со связанными задачами:
    relations = TaskRelation.objects.all()
    related_tasks = {}
    for relation in relations:
        related_tasks[relation.dependant_task] = relation.linked_task
    context = {"tasks_list": tasks_list, "theme": theme, "related_tasks": related_tasks}
    user = request.user
    if user.is_authenticated():
        # определяем, выполнены ли задачи текущим юзером, если да - передаем выполненные задачи в контексте:
        finished_statuses = Status.objects.filter(state='FINISHED', user=user)
        finished_tasks = []
        for status in finished_statuses:
            finished_tasks.append(status.task)
        context['finished_tasks'] = finished_tasks
    return render(request, 'tasks/list_of_tasks.html', context)


def tasks(request):
    tasks_list = Task.objects.all().order_by('code')
    # задаем словарь со связанными задачами:
    relations = TaskRelation.objects.all()
    related_tasks = {}
    for relation in relations:
        related_tasks[relation.dependant_task] = relation.linked_task
    context = {"tasks_list": tasks_list, "related_tasks": related_tasks}
    user = request.user
    if user.is_authenticated():
        # определяем, выполнены ли задачи текущим юзером, если да - передаем выполненные задачи в контексте:
        finished_statuses = Status.objects.filter(state='FINISHED', user=user)
        finished_tasks = []
        for status in finished_statuses:
            finished_tasks.append(status.task)
        context['finished_tasks'] = finished_tasks
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
    task_theme_code = code.split('-')[0]
    task_code = code.split('-')[1]
    try:
        theme = Theme.objects.get(theme_code=task_theme_code)
        task = Task.objects.get(code=task_code,task_theme=theme)
    except ObjectDoesNotExist:
        print("Task with such code or theme doesn't exist")
        return HttpResponseRedirect(reverse('tasks:tasks'))
    except MultipleObjectsReturned:
        print("More than one task exists or themes with such code")
        return HttpResponseRedirect(reverse('tasks:tasks'))
    return HttpResponseRedirect(reverse('tasks:task', args=(task.id,)))


class TaskDetailView(DetailView):
    model = Task
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
        self.template_name = self.template_name + task.task_theme.theme_code + "-" + task.code + ".html"
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