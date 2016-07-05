from django import forms
from .models import Goal
from django.template.defaultfilters import mark_safe


class GoalForm(forms.ModelForm):

    class Meta:
        model = Goal
        fields = [
            'date',
            'sold_by',
            'goal_type',
            'goal',
            'note1',
            'note2',
            'note3'
        ]

