from django.db import models
from django.utils import timezone
from client.models import Trainer



class Record(models.Model):
    date = models.DateField(blank=False, default=timezone.now)
    gross_sale = models.FloatField(blank=False,null=False)
    cash_recieved = models.FloatField(blank=True)
    eft_added = models.FloatField(blank=True,null=True)
    eft_loss = models.FloatField(blank=True,null=True)
    sold_by = models.ForeignKey(Trainer, default=2)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    # def __str__(self):
    #     return self.pk


