from django.conf.urls import url

from . import views
from .views import TaskDetailView

app_name = 'tasks'
urlpatterns = [
    # ex: /events/
    url(r'^$', views.tasks, name='tasks'),
    url(r'^(?P<pk>[0-9]+)/$', TaskDetailView.as_view(), name='task'),
]

