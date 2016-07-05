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
from .forms import AppointmentForm
from .models import appointment
from client.models import Client, Lead, Trainer, Program
from target.models import Target_type,Goal
from sales.models import Record
from django.db.models import Avg, Max, Min,F, FloatField, Sum,Count
import datetime


def add_appointment(request):

    if request.user.is_authenticated():
        form = AppointmentForm(request.POST or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()

        context = {
        "form": form
        }
        return render(request, 'templates/form_appointment.html', context)

    else:
        return render(request, 'base.html',{})

def appointment_info(request):

    if request.user.is_authenticated():

        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %y")

            if var in list_of_filters:
                continue
            else:
                temp=dict()
                temp['filter']=var
                temp['year']=str(i.year)
                temp['month']= str("0"+str(i.month))[-2:]

                list_of_filters.append(var)
                list_of_slicer.append(temp)


        months = appointment.objects.values_list('date',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/appointment_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def appointment_table(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        tracking_info=[]
        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %y")

            if var in list_of_filters:
                continue
            else:
                temp=dict()
                temp['filter']=var
                temp['year']=str(i.year)
                temp['month']= str("0"+str(i.month))[-2:]

                list_of_filters.append(var)
                list_of_slicer.append(temp)


        month_rep = int(slicer2)
        year_rep=int(slicer1)
        repoting_date = datetime.datetime(year_rep, month_rep, 1, 0, 0, 0)

        Appointment_filtered=appointment.objects.filter(date__month=slicer2,date__year=slicer1)
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        requested = Appointment_filtered.aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'))
        visits =sales_filtered.aggregate(shows=Sum('consults_attended'))



        temp=dict()
        temp['shows_percentage']=round(100*visits['shows']/requested['requested'],1)
        temp['cancelled']=round(100*requested['cancelled']/requested['requested'],1)
        temp['closed']=round(100*requested['closed']/requested['requested'],1)
        temp['no_show']=round(100*requested['no_show']/requested['requested'],1)
        temp['rescheduled']=round(100*requested['rescheduled']/requested['requested'],1)

        temp1=dict()
        temp1['shows']=visits['shows']
        temp1['cancelled']=requested['cancelled']
        temp1['closed']=requested['closed']
        temp1['no_show']=requested['no_show']
        temp1['rescheduled']=requested['rescheduled']




        return render(request, 'templates/table_appointment.html', {'tracking_info': temp, 'tracking_sum': temp1,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                               'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

def appointment_chart_info(request):

    if request.user.is_authenticated():

        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %y")

            if var in list_of_filters:
                continue
            else:
                temp=dict()
                temp['filter']=var
                temp['year']=str(i.year)
                temp['month']= str("0"+str(i.month))[-2:]

                list_of_filters.append(var)
                list_of_slicer.append(temp)


        months = appointment.objects.values_list('date',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/appointment_chart_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def appointment_chart(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        tracking_info=[]
        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %y")

            if var in list_of_filters:
                continue
            else:
                temp=dict()
                temp['filter']=var
                temp['year']=str(i.year)
                temp['month']= str("0"+str(i.month))[-2:]

                list_of_filters.append(var)
                list_of_slicer.append(temp)


        month_rep = int(slicer2)
        year_rep=int(slicer1)
        repoting_date = datetime.datetime(year_rep, month_rep, 1, 0, 0, 0)

        Appointment_filtered=appointment.objects.filter(date__month=slicer2,date__year=slicer1)
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        requested = Appointment_filtered.aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'))
        visits =sales_filtered.aggregate(shows=Sum('consults_attended'))



        temp=dict()
        temp['shows_percentage']=round(100*visits['shows']/requested['requested'],1)
        temp['cancelled']=round(100*requested['cancelled']/requested['requested'],1)
        temp['closed']=round(100*requested['closed']/requested['requested'],1)
        temp['no_show']=round(100*requested['no_show']/requested['requested'],1)
        temp['rescheduled']=round(100*requested['rescheduled']/requested['requested'],1)

        temp1=dict()
        temp1['shows']=visits['shows']
        temp1['cancelled']=requested['cancelled']
        temp1['closed']=requested['closed']
        temp1['no_show']=requested['no_show']
        temp1['rescheduled']=requested['rescheduled']




        return render(request, 'templates/appointment_chart.html', {'tracking_info': temp, 'tracking_sum': temp1,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                               'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})
