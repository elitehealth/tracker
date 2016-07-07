from django.db import models
from django.utils import timezone



class Trainer(models.Model):
    name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return '%s' % (self.name)



class Program(models.Model):
    name = models.CharField(max_length=75)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return '%s' % (self.name)


class Lead(models.Model):
    name = models.CharField(max_length=75)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return '%s' % (self.name)



class Client(models.Model):
    client_name = models.CharField(max_length=100, blank=False)
    date_sign_up = models.DateField(blank=False, default=timezone.now)
    program_sold = models.ForeignKey(Program)
    gross_sale = models.FloatField(blank=False,null=False)
    cash_recieved = models.FloatField()
    eft_added = models.FloatField()
    eft_loss = models.FloatField()
    lead_source = models.ForeignKey(Lead)
    date_input = models.DateField(default=timezone.now, blank=False)
    sold_by = models.ForeignKey(Trainer)
    note1 = models.CharField(max_length=100, blank=True)
    note2 = models.CharField(max_length=100, blank=True)
    note3 = models.TextField(blank=True)
    def __str__(self):
        return self.client_name


