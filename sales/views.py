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
from .forms import SalesForm
from django.contrib.auth import models
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.core import serializers
from django.db import connection
from django.shortcuts import render
from .models import Record
from client.models import Client, Lead, Trainer, Program
from django.db.models import Avg, Max,F, FloatField, Sum,Count
import datetime


def add_sales(request):

    if request.user.is_authenticated():
        form = SalesForm(request.POST or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()

        context = {
        "form": form
        }
        return render(request, 'templates/form_sales.html', context)

    else:
        return render(request, 'base.html',{})


def sales_info(request):

    if request.user.is_authenticated():

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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


        months = Record.objects.values_list('date',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/sales_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def sales_chart_info(request):

    if request.user.is_authenticated():

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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


        months = Record.objects.values_list('date',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/sales_chart_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})


def sales_table(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_dates=[]
        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        for i in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))
            week=str()
            if sold_dates[i].day >=16:
                week ="After 15"
            else:
                week="Before 15"

            temp=dict()
            temp['date']=sold_dates[i]
            temp['week']=week
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            sales_dates.append(temp)

        return render(request, 'templates/table_sales.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})



def chart(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_dates=[]
        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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


        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)

        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('date')
        for i in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))

            temp=dict()
            temp['date']=sold_dates[i].strftime("%a, %d")
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            sales_dates.append(temp)
        return render(request, 'templates/sales_chart.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

