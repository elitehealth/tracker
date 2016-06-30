from django import forms
from .models import Client
from django.template.defaultfilters import mark_safe


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = [
            'client_name',
            'date_sign_up',
            'program_sold',
            'gross_sale',
            'cash_recieved',
            'eft_added',
            'eft_loss',
            'lead_source',
            'sold_by',
            'note1',
            'note2',
            'note3'
        ]

