from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    code = models.CharField(max_length=200, default="TASK-01")
    title = models.CharField(max_length=200, default="This is default task title")
    description = models.TextField(max_length=2000, default="This is default task description")

    def __str__(self):
        return self.title