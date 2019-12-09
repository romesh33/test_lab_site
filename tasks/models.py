from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Theme(models.Model):
    description = models.TextField(max_length=2000, default="Описание темы по умолчанию")
    THEMES_CHOICES = (
        ('API', 'API'),
        ('ET', 'ET'),
        ('IOT', 'IOT'),
        ('GAMES', 'GAMES'),
        ('HIDDEN', 'HIDDEN')
    )
    theme_code = models.CharField(max_length=10,
                                      choices=THEMES_CHOICES,
                                      default='API')
    THEMES_STATUS_CHOICES = (
        ('in_progress', 'IN PROGRESS'),
        ('coming_soon', 'COMING SOON'),
        ('finished', 'FINISHED'),
    )
    theme_status = models.CharField(max_length=15,
                                      choices=THEMES_STATUS_CHOICES,
                                      default='in_progress')
    def __str__(self):
        return self.theme_code + ": " + self.theme_status

class Task(models.Model):
    code = models.CharField(max_length=5, default="01")
    title = models.CharField(max_length=200, default="Заголовок задачи по умолчанию")
    description = models.TextField(max_length=2000, default="Описание задачи по умолчанию")
    task_theme = models.ForeignKey(Theme, related_name="task_theme", null=False, on_delete=models.PROTECT)
    TASK_LEVEL = (
        ('simple', 'simple'),
        ('average', 'average'),
        ('hard', 'hard'),
    )
    level = models.CharField(max_length=10,
                                      choices=TASK_LEVEL,
                                      default='simple')
    time = models.IntegerField(default=15)

    def __str__(self):
        return self.task_theme.theme_code + "-" + self.code + ": " + self.title

    class Meta:
        ordering = ["code"]

class TaskRelation(models.Model):
    dependant_task = models.ForeignKey(Task, related_name="dependant_task", on_delete=models.PROTECT)
    linked_task = models.ForeignKey(Task, related_name="linked_task", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.linked_task.code + ": " + self.linked_task.title + " -> " + self.dependant_task.code + ": " + self.dependant_task.title
        #return self.dependant_task.code + ": " + self.dependant_task.title


class Status(models.Model):
    task = models.ForeignKey(Task, related_name="task", on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="user", on_delete=models.PROTECT)
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
        return self.user.username + " - " + self.task.task_theme.theme_code + "-" + self.task.code + " - " + self.state