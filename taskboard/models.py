from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Board(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, through='BoardAccess')

class BoardAccess(models.Model):
    ROLES = (
        ('creator', 'Creator'),
        ('coordinator', 'Coordinator'),
        ('standard', 'Standard'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

class List(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists')
    order = models.PositiveIntegerField(default=0) 

    class Meta:
        ordering = ['order']
        unique_together = ('board', 'order')

class Task(models.Model):
    name = models.CharField(max_length=100)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='tasks')
    assigned = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    order = models.PositiveIntegerField(default=0) 

    class Meta:
        ordering = ['order']
        unique_together = ('list', 'order')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
