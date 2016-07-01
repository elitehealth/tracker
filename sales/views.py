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
from target.models import Target_type,Goal
from django.db.models import Avg, Max, Min,F, FloatField, Sum,Count
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

def sales_table(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_dates=[]
        sales_period=[]
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

        gross_period_1 =float()
        gross_period_2 =float()
        cash_period_1 =float()
        cash_period_2 =float()
        net_eft_period_1 =float()
        net_eft_period_2 =float()
        temp1=dict()



        for i in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))
            temp=dict()
            temp1=dict()

            if sold_dates[i].day<=15:
                gross_period_1=gross_period_1+gross_sale['sales']
                cash_period_1=cash_period_1+cash['cash']
                net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
            else:
                gross_period_2=gross_period_2+gross_sale['sales']
                cash_period_2=cash_period_2+cash['cash']
                net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']


            temp['date']=sold_dates[i]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss


            sales_dates.append(temp)

        temp1['period1_gross']=gross_period_1
        temp1['period2_gross']=gross_period_2
        temp1['period1_cash']=cash_period_1
        temp1['period2_cash']=cash_period_2
        temp1['period1_net']=net_eft_period_1
        temp1['period2_net']=net_eft_period_2
        sales_period.append(temp1)

        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            # In the DB id of gross sale is 6
            gross_target_monthly=float(Target_type.objects.filter(id=6).values_list('monthly_goal')[0][0])

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            # In the DB id of cash is 7
            cash_target_monthly=float(Target_type.objects.filter(id=7).values_list('monthly_goal')[0][0])

            net_eft = sales_filtered.filter(sold_by=trainer[i]).aggregate(net_eft=Sum('eft_added')-Sum('eft_loss'))
            net_eft_target_monthly=float(Target_type.objects.filter(id=8).values_list('monthly_goal')[0][0])


            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['gross_target']=gross_target_monthly
            temp['gross_KPI']=round(100*gross_sale['sales']/gross_target_monthly,0)
            temp['cash']=cash
            temp['cash_target']=cash_target_monthly
            temp['cash_KPI']=str(round(100*cash['cash']/cash_target_monthly,0))+"%"
            temp['net_eft']=net_eft
            temp['net_eft_target']=net_eft_target_monthly
            temp['net_eft_KPI']=str(round(100*net_eft['net_eft']/net_eft_target_monthly,0))+"%"
            sales_trainer.append(temp)



        return render(request, 'templates/table_sales.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'list_of_slicer': list_of_slicer,
                                                              'sales_period': sales_period,
                                                              'sales_trainer': sales_trainer})

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
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'),min_sales=Min('gross_sale'), max_sales=Max('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'),min_cash=Min('cash_recieved'), max_cash=Max('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'),min_eft_added=Min('eft_added'), max_eft_added=Max('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'),min_eft_loss=Min('eft_loss'), max_eft_loss=Max('eft_loss'))

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


def sales_kpi(request):

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

        return render(request, 'templates/sales_kpi.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def sales_kpi_table(request,slicer1,slicer2):

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

        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            # In the DB id of gross sale is 6
            gross_target_monthly=float(Target_type.objects.filter(id=6).values_list('monthly_goal')[0][0])

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            # In the DB id of cash is 7
            cash_target_monthly=float(Target_type.objects.filter(id=7).values_list('monthly_goal')[0][0])

            net_eft = sales_filtered.filter(sold_by=trainer[i]).aggregate(net_eft=Sum('eft_added')-Sum('eft_loss'))
            net_eft_target_monthly=float(Target_type.objects.filter(id=8).values_list('monthly_goal')[0][0])


            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['gross_target']=gross_target_monthly
            temp['gross_KPI']=round(100*gross_sale['sales']/gross_target_monthly,0)
            temp['cash']=cash
            temp['cash_target']=cash_target_monthly
            temp['cash_KPI']=str(round(100*cash['cash']/cash_target_monthly,0))+"%"
            temp['net_eft']=net_eft
            temp['net_eft_target']=net_eft_target_monthly
            temp['net_eft_KPI']=str(round(100*net_eft['net_eft']/net_eft_target_monthly,0))+"%"
            sales_trainer.append(temp)



        return render(request, 'templates/table_kpi.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'list_of_slicer': list_of_slicer,
                                                              'sales_trainer': sales_trainer})

    else:
        return render(request, 'base.html', {})


def sales_kpi_chart_info(request):

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

        return render(request, 'templates/sales_kpi_chart_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def sales_kpi_chart(request,slicer1,slicer2):

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

        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            # In the DB id of gross sale is 6
            gross_target_monthly=float(Target_type.objects.filter(id=6).values_list('monthly_goal')[0][0])

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            # In the DB id of cash is 7
            cash_target_monthly=float(Target_type.objects.filter(id=7).values_list('monthly_goal')[0][0])

            net_eft = sales_filtered.filter(sold_by=trainer[i]).aggregate(net_eft=Sum('eft_added')-Sum('eft_loss'))
            net_eft_target_monthly=float(Target_type.objects.filter(id=8).values_list('monthly_goal')[0][0])


            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['gross_target']=gross_target_monthly
            temp['gross_KPI']=round(100*gross_sale['sales']/gross_target_monthly,0)
            temp['cash']=cash
            temp['cash_target']=cash_target_monthly
            temp['cash_KPI']=round(100*cash['cash']/cash_target_monthly,0)
            temp['net_eft']=net_eft
            temp['net_eft_target']=net_eft_target_monthly
            temp['net_eft_KPI']=round(100*net_eft['net_eft']/net_eft_target_monthly,0)
            sales_trainer.append(temp)



        return render(request, 'templates/sales_kpi_chart.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'list_of_slicer': list_of_slicer,
                                                              'sales_trainer': sales_trainer})

    else:
        return render(request, 'base.html', {})


