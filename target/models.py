from django.db import models
from django.utils import timezone
from client.models import Trainer




class Target_type(models.Model):
    target_type = models.CharField(max_length=75)
    monthly_goal = models.CharField(max_length=100, blank=True)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return '%s' % (self.target_type)


class Goal(models.Model):
    date = models.DateField(blank=False)
    sold_by = models.ForeignKey(Trainer)
    goal_type = models.ForeignKey(Target_type)
    goal = models.FloatField(blank=True,null=True)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    note3 = models.TextField(blank=True)
    # def __str__(self):
    #     return self.pk


