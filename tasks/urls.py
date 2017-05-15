from django.conf.urls import url

from . import views
from .views import TaskDetailView
from django.contrib.auth.decorators import login_required

app_name = 'tasks'
urlpatterns = [
    url(r'^$', views.tasks, name='tasks'),
    # ex: /theme/
    url(r'^theme/$', views.tasks, name='tasks'),
    # ex: /theme/API
    url(r'^theme/(?P<theme>[^0-9]+)/$', views.theme_tasks, name='theme_tasks'),
    # ex: /10
    url(r'^(?P<pk>[0-9]+)/$', login_required(TaskDetailView.as_view()), name='task'),
    # ex: /API-01:
    url(r'^(?P<code>([^0-9]+)-([0-9]+))/$', views.task_by_code, name='task_by_code'),
    # ex: /10/start
    url(r'^(?P<task_id>[0-9]+)/start$', views.start, name='start'),
    # ex: /10/stop
    url(r'^(?P<task_id>[0-9]+)/stop$', views.stop, name='stop'),
    # ex: /10/continue
    url(r'^(?P<task_id>[0-9]+)/come_back$', views.come_back, name='come_back'),
    # ex: /10/finish
    url(r'^(?P<task_id>[0-9]+)/finish$', views.finish, name='finish'),
]

