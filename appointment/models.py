from django.db import models
from django.utils import timezone
from client.models import Trainer



class appointment(models.Model):
    date = models.DateField(blank=False, default=timezone.now)
    consultations_requested = models.IntegerField(blank=False)
    consultations_scheduled = models.IntegerField(blank=False, null=False)
    consultations_cancelled = models.IntegerField(blank=False, null=False)
    consultations_closed = models.IntegerField(blank=False, null=False)
    consultations_no_show = models.IntegerField(blank=False, null=False)
    consultations_rescheduled = models.IntegerField(blank=False, null=False)
    consultations_attended = models.IntegerField(blank=False, null=False)
    input_by = models.ForeignKey(Trainer, default=1)
    note1 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.note1