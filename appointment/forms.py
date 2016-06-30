from django import forms
from .models import appointment
from django.template.defaultfilters import mark_safe


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = appointment
        fields = [
            'date',
            'sold_by',
            'consultation_scheduled',
            'consultation_showed',
            'consultation_closed',
            'sold_by',
            'consult_no_call_no_show',
            'consult_cancelled_rescheduled',
            'consult_cancelled'
        ]

