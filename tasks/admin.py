from django.contrib import admin
from .models import Task, TaskRelation, Status

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskRelation)
admin.site.register(Status)
