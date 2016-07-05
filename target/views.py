from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.generic import ListView
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import redirect,  get_object_or_404
from django.contrib import auth
from django.contrib.auth import models
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.db import connection
import sqlite3, random, os, json
from django.shortcuts import render
from .forms import GoalForm
from django.contrib.auth import models
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.core import serializers
from django.db import connection
from django.shortcuts import render
from .models import Goal
from client.models import Client, Lead, Trainer, Program
from target.models import Target_type,Goal
from django.db.models import Avg, Max, Min,F, FloatField, Sum,Count
import datetime


def add_goal(request):

    if request.user.is_authenticated():
        form = GoalForm(request.POST or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()

        context = {
        "form": form
        }
        return render(request, 'templates/form_goal.html', context)

    else:
        return render(request, 'base.html',{})

