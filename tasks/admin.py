from django.contrib import admin
from .models import Task, TaskRelation, Status, Theme

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskRelation)
admin.site.register(Status)
admin.site.register(Theme)
