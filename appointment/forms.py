from django import forms
from .models import appointment
from django.template.defaultfilters import mark_safe


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = appointment
        fields = [
            'date',
            'consultations_requested',
            'consultations_scheduled',
            'consultations_cancelled',
            'consultations_closed',
            'consultations_no_show',
            'consultations_rescheduled',
            'consultations_attended',
            'input_by',
            'note1',
        ]

