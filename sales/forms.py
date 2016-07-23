from django import forms
from .models import Record
from django.template.defaultfilters import mark_safe


class SalesForm(forms.ModelForm):

    class Meta:
        model = Record
        fields = [
            'date',
            'gross_sale',
            'cash_recieved',
            'eft_added',
            'eft_loss',
            'sold_by',
            'note1',
            'note2',
        ]


