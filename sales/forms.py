from django import forms
from .models import Record
from django.template.defaultfilters import mark_safe


class SalesForm(forms.ModelForm):

    class Meta:
        model = Record
        fields = [
            'date',
            'consults_attended',
            'consults_closed',
            'gross_sale',
            'cash_recieved',
            'eft_added',
            'eft_loss',
            'note1',
            'note2',
            'note3'
        ]


