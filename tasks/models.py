from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    code = models.CharField(max_length=200, default="TASK-01")
    title = models.CharField(max_length=200, default="This is default task title")
    description = models.TextField(max_length=2000, default="This is default task description")
    TASK_THEMES_CHOICES = (
        ('API', 'API'),
        ('ET', 'ET'),
        ('IOT', 'IOT'),
        ('games', 'games'),
    )
    task_theme = models.CharField(max_length=5,
                                      choices=TASK_THEMES_CHOICES,
                                      default='API')

    def __str__(self):
        return self.title

class TaskRelation(models.Model):
    dependant_task = models.ForeignKey(Task, related_name="dependant_task")
    linked_tasks = models.ManyToManyField(Task, related_name="linked_tasks")

    def __str__(self):
        return 'Связь между задачами'


class Status(models.Model):
    task = models.ForeignKey(Task, related_name="task")
    user = models.ForeignKey(User, related_name="user")
    start_time = models.DateTimeField('start_time', auto_now=False, null=True)
    stop_time = models.DateTimeField('stop_time', auto_now=False, null=True)
    comeback_time = models.DateTimeField('comeback_time', auto_now=False, null=True)
    finish_time = models.DateTimeField('finish_time', auto_now=False, null=True)
    duration = models.DurationField('duration', default=timedelta(minutes=0))
    STATE_CHOICES = (
        ('IDLE', 'IDLE'),
        ('RUNNING', 'RUNNING'),
        ('STOPPED', 'STOPPED'),
        ('FINISHED', 'FINISHED'),
    )
    state = models.CharField(max_length=10,
                                      choices=STATE_CHOICES,
                                      default='IDLE')

    def __str__(self):
        return self.state