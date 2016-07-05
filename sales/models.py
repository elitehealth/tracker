from django.db import models
from django.utils import timezone
from client.models import Trainer



class Record(models.Model):
    date = models.DateField(blank=False)
    consults_attended = models.IntegerField(blank=False,null=False)
    consults_closed = models.IntegerField(blank=False)
    gross_sale = models.FloatField(blank=False,null=False)
    cash_recieved = models.FloatField(blank=True)
    eft_added = models.FloatField(blank=True,null=True)
    eft_loss = models.FloatField(blank=True,null=True)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    note3 = models.TextField(blank=True)
    # def __str__(self):
    #     return self.pk


