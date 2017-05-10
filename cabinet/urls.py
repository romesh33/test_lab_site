from django.conf.urls import url

from . import views

app_name = 'cabinet'
urlpatterns = [
    # ex: /cabinet/4
    url(r'^(?P<user_id>[0-9]+)/$', views.viewCabinet, name='view_cabinet'),
    # ex: /cabinet/4/edit
    url(r'^(?P<user_id>[0-9]+)/edit/$', views.editProfile, name='edit_profile'),
]