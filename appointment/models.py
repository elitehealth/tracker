from django.db import models
from django.utils import timezone
from client.models import Trainer



class appointment(models.Model):
    date = models.DateField(blank=False)
    sold_by = models.ForeignKey(Trainer)
    consultation_scheduled = models.IntegerField(blank=False,null=False)
    consultation_showed = models.IntegerField(blank=False,null=False)
    consultation_closed = models.IntegerField(blank=False,null=False)
    consult_no_call_no_show = models.IntegerField(blank=False,null=False)
    consult_cancelled_rescheduled = models.IntegerField(blank=False,null=False)
    consult_cancelled = models.IntegerField(blank=False,null=False)

    # def __str__(self):
    #     return self.pk


