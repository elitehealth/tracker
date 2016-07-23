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
            var=i.strftime("%B, %Y")

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
        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %Y")

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
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))

        requested_1 = Appointment_filtered.filter(date__lte=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0)).aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))

        requested_2 = Appointment_filtered.filter(date__gt=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0)).aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))
        temp=dict()
        temp1=dict()

        if requested['requested'] is None:
            temp1['shows']=0
            temp1['cancelled']=0
            temp1['closed']=0
            temp1['no_show']=0
            temp1['rescheduled']=0
            temp['shows_percentage']=0
            temp['cancelled']=0
            temp['closed']=0
            temp['no_show']=0
            temp['rescheduled']=0

        else:
            temp1['shows']=requested['attended']
            temp1['cancelled']=requested['cancelled']
            temp1['closed']=requested['closed']
            temp1['no_show']=requested['no_show']
            temp1['rescheduled']=requested['rescheduled']
            temp['shows_percentage']=round(100*requested['attended']/requested['requested'],1)
            temp['cancelled']=round(100*requested['cancelled']/requested['requested'],1)
            temp['closed']=round(100*requested['closed']/requested['requested'],1)
            temp['no_show']=round(100*requested['no_show']/requested['requested'],1)
            temp['rescheduled']=round(100*requested['rescheduled']/requested['requested'],1)

        if requested_1['requested'] is None:
            temp1['shows_1']=0
            temp1['cancelled_1']=0
            temp1['closed_1']=0
            temp1['no_show_1']=0
            temp1['rescheduled_1']=0
            temp['shows_percentage_1']=0
            temp['cancelled_1']=0
            temp['closed_1']=0
            temp['no_show_1']=0
            temp['rescheduled_1']=0

        else:
            temp['shows_percentage_1']=round(100*requested_1['attended']/requested_1['requested'],1)
            temp['cancelled_1']=round(100*requested_1['cancelled']/requested_1['requested'],1)
            temp['closed_1']=round(100*requested_1['closed']/requested_1['requested'],1)
            temp['no_show_1']=round(100*requested_1['no_show']/requested_1['requested'],1)
            temp['rescheduled_1']=round(100*requested_1['rescheduled']/requested_1['requested'],1)
            temp1['shows_1']=requested_1['attended']
            temp1['cancelled_1']=requested_1['cancelled']
            temp1['closed_1']=requested_1['closed']
            temp1['no_show_1']=requested_1['no_show']
            temp1['rescheduled_1']=requested_1['rescheduled']

        if requested_2['requested'] is None:
            temp1['shows_2']=0
            temp1['cancelled_2']=0
            temp1['closed_2']=0
            temp1['no_show_2']=0
            temp1['rescheduled_2']=0
            temp['shows_percentage_2']=0
            temp['cancelled_2']=0
            temp['closed_2']=0
            temp['no_show_2']=0
            temp['rescheduled_2']=0

        else:
            temp['shows_percentage_2']=round(100*requested_2['attended']/requested_2['requested'],1)
            temp['cancelled_2']=round(100*requested_2['cancelled']/requested_2['requested'],1)
            temp['closed_2']=round(100*requested_2['closed']/requested_2['requested'],1)
            temp['no_show_2']=round(100*requested_2['no_show']/requested_2['requested'],1)
            temp['rescheduled_2']=round(100*requested_2['rescheduled']/requested_2['requested'],1)
            temp1['shows_2']=requested_2['attended']
            temp1['cancelled_2']=requested_2['cancelled']
            temp1['closed_2']=requested_2['closed']
            temp1['no_show_2']=requested_2['no_show']
            temp1['rescheduled_2']=requested_2['rescheduled']



        return render(request, 'templates/table_appointment.html', {'tracking_info': temp, 'tracking_sum': temp1,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                               'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

def appointment_chart_info(request):

    if request.user.is_authenticated():

        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %Y")

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
        months = appointment.objects.values_list('date',flat=True).distinct().order_by('-date')
        list_of_filters = []
        list_of_slicer=[]

        for i in months:
            var=i.strftime("%B, %Y")

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
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))

        requested_1 = Appointment_filtered.filter(date__lte=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0)).aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))

        requested_2 = Appointment_filtered.filter(date__gt=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0)).aggregate(requested=Sum('consultations_requested'),
                                                   scheduled=Sum('consultations_scheduled'),
                                                   cancelled=Sum('consultations_cancelled'),
                                                   closed=Sum('consultations_closed'),
                                                   no_show=Sum('consultations_no_show'),
                                                   rescheduled=Sum('consultations_rescheduled'),
                                                   attended=Sum('consultations_attended'))

        temp=dict()
        temp1=dict()

        if requested['requested'] is None:
            temp1['shows']=0
            temp1['cancelled']=0
            temp1['closed']=0
            temp1['no_show']=0
            temp1['rescheduled']=0
            temp['shows_percentage']=0
            temp['cancelled']=0
            temp['closed']=0
            temp['no_show']=0
            temp['rescheduled']=0

        else:
            temp1['shows']=requested['attended']
            temp1['cancelled']=requested['cancelled']
            temp1['closed']=requested['closed']
            temp1['no_show']=requested['no_show']
            temp1['rescheduled']=requested['rescheduled']
            temp['shows_percentage']=round(100*requested['attended']/requested['requested'],1)
            temp['cancelled']=round(100*requested['cancelled']/requested['requested'],1)
            temp['closed']=round(100*requested['closed']/requested['requested'],1)
            temp['no_show']=round(100*requested['no_show']/requested['requested'],1)
            temp['rescheduled']=round(100*requested['rescheduled']/requested['requested'],1)

        if requested_1['requested'] is None:
            temp1['shows_1']=0
            temp1['cancelled_1']=0
            temp1['closed_1']=0
            temp1['no_show_1']=0
            temp1['rescheduled_1']=0
            temp['shows_percentage_1']=0
            temp['cancelled_1']=0
            temp['closed_1']=0
            temp['no_show_1']=0
            temp['rescheduled_1']=0

        else:
            temp['shows_percentage_1']=round(100*requested_1['attended']/requested_1['requested'],1)
            temp['cancelled_1']=round(100*requested_1['cancelled']/requested_1['requested'],1)
            temp['closed_1']=round(100*requested_1['closed']/requested_1['requested'],1)
            temp['no_show_1']=round(100*requested_1['no_show']/requested_1['requested'],1)
            temp['rescheduled_1']=round(100*requested_1['rescheduled']/requested_1['requested'],1)
            temp1['shows_1']=requested_1['attended']
            temp1['cancelled_1']=requested_1['cancelled']
            temp1['closed_1']=requested_1['closed']
            temp1['no_show_1']=requested_1['no_show']
            temp1['rescheduled_1']=requested_1['rescheduled']

        if requested_2['requested'] is None:
            temp1['shows_2']=0
            temp1['cancelled_2']=0
            temp1['closed_2']=0
            temp1['no_show_2']=0
            temp1['rescheduled_2']=0
            temp['shows_percentage_2']=0
            temp['cancelled_2']=0
            temp['closed_2']=0
            temp['no_show_2']=0
            temp['rescheduled_2']=0

        else:
            temp['shows_percentage_2']=round(100*requested_2['attended']/requested_2['requested'],1)
            temp['cancelled_2']=round(100*requested_2['cancelled']/requested_2['requested'],1)
            temp['closed_2']=round(100*requested_2['closed']/requested_2['requested'],1)
            temp['no_show_2']=round(100*requested_2['no_show']/requested_2['requested'],1)
            temp['rescheduled_2']=round(100*requested_2['rescheduled']/requested_2['requested'],1)
            temp1['shows_2']=requested_2['attended']
            temp1['cancelled_2']=requested_2['cancelled']
            temp1['closed_2']=requested_2['closed']
            temp1['no_show_2']=requested_2['no_show']
            temp1['rescheduled_2']=requested_2['rescheduled']

        return render(request, 'templates/appointment_chart.html', {'tracking_info': temp, 'tracking_sum': temp1,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                               'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

