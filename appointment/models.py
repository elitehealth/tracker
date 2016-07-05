from django.db import models
from django.utils import timezone
from client.models import Trainer



class appointment(models.Model):
    date = models.DateField(blank=False)
    consultations_requested = models.IntegerField(blank=False)
    consultations_scheduled = models.IntegerField(blank=False,null=False)
    consultations_cancelled = models.IntegerField(blank=False,null=False)
    consultations_closed = models.IntegerField(blank=False,null=False)
    consultations_no_show = models.IntegerField(blank=False,null=False)
    consultations_rescheduled = models.IntegerField(blank=False,null=False)

    # def __str__(self):
    #     return self.pk

