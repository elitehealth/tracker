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
from django.core import serializers
from django.db import connection
import sqlite3, random, os, json
from django.shortcuts import render
from .forms import ClientForm
from .models import Client, Lead, Trainer, Program
from django.db.models import Avg, Max,F, FloatField, Sum,Count
import datetime
from sales.models import Record
from target.models import Target_type,Goal
import calendar

def home(request):
    return render(request, 'base.html',{})


def client_info(request):

    if request.user.is_authenticated():

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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


        months = Client.objects.values_list('date_sign_up',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/client_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def client_chart_info(request):

    if request.user.is_authenticated():

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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


        months = Client.objects.values_list('date_sign_up',flat=True).distinct()
        list_of_month = []
        for i in months:
            if i.month in list_of_month:
                continue
            else:
                list_of_month.append(i.month)

        return render(request, 'templates/client_chart_info.html', {'list_of_slicer': list_of_slicer})

    else:
        return render(request, 'base.html', {})

def direct(request):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_sum=[]
        sales_dates=[]

        repoting_date = datetime.datetime.now()
        sales_filtered=Client.objects.filter(date_sign_up__month=repoting_date.month,date_sign_up__year=repoting_date.year)
        max_days=calendar.monthrange(repoting_date.year,repoting_date.month)[1]
        completed_days=repoting_date.day
        operating_days=max_days-completed_days

        gross_sale = sales_filtered.aggregate(sales=Sum('gross_sale'))
        gross_speed= round(gross_sale['sales']/completed_days,0)
        gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
        gross_gap=gross_target['gross_target']-gross_sale['sales']
        gross_speed_required= round(gross_gap/operating_days,0)
        gross_speed_increase = round(100*(gross_speed_required/gross_speed-1),2)

        cash = sales_filtered.aggregate(cash=Sum('cash_recieved'))
        cash_speed= round(cash['cash']/completed_days,0)
        cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
        cash_gap=cash_target['cash_target']-cash['cash']
        cash_speed_required= round(cash_gap/operating_days,0)
        cash_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)

        eft_added = sales_filtered.aggregate(eft_added=Sum('eft_added'))
        eft_loss = sales_filtered.aggregate(eft_loss=Sum('eft_loss'))
        net_eft=eft_added['eft_added']-eft_loss['eft_loss']
        net_eft_speed= round(net_eft/completed_days,0)
        net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
        net_eft_gap=net_eft_target['net_eft_target']-net_eft
        net_eft_speed_required= round(net_eft_gap/operating_days,0)
        net_eft_speed_increase = round(100*(net_eft_speed_required/net_eft_speed-1),2)

        program = sales_filtered.aggregate(program=Count('program_sold'))
        program_speed= round(program['program']/completed_days,0)
        program_target=Target_type.objects.filter(id=5).aggregate(program_target=Sum('monthly_goal'))
        program_gap=program_target['program_target']-program['program']
        program_speed_required= round(program_gap/operating_days,2)
        program_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)

        temp0=dict()
        temp0['gross_sale']=int(gross_sale['sales'])
        temp0['gross_speed']=int(gross_speed)
        temp0['gross_gap']=int(gross_gap)
        temp0['gross_speed_required']=gross_speed_required
        temp0['gross_speed_increase']=gross_speed_increase

        temp0['cash']=int(cash['cash'])
        temp0['cash_speed']=cash_speed
        temp0['cash_gap']=cash_gap
        temp0['cash_speed_required']=cash_speed_required
        temp0['cash_speed_increase']=cash_speed_increase

        temp0['net_eft']=int(net_eft)
        temp0['net_eft_speed']=int(net_eft_speed)
        temp0['net_eft_gap']=net_eft_gap
        temp0['net_eft_speed_required']=net_eft_speed_required
        temp0['net_eft_speed_increase']=net_eft_speed_increase

        temp0['program']=int(program['program'])
        temp0['program_speed']=program_speed
        temp0['program_gap']=program_gap
        temp0['program_speed_required']=program_speed_required
        temp0['program_speed_increase']=program_speed_increase

        sales_sum.append(temp0)


        sales_filtered_sales=Record.objects.filter(date__month=repoting_date.month,date__year=repoting_date.year)
        sold_dates_sales=sales_filtered_sales.values_list('date', flat=True).distinct().order_by('-date')

        for i in range(len(sold_dates_sales)):
            gross_sale = sales_filtered_sales.filter(date=sold_dates_sales[i]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered_sales.filter(date=sold_dates_sales[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered_sales.filter(date=sold_dates_sales[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered_sales.filter(date=sold_dates_sales[i]).aggregate(eft_loss=Sum('eft_loss'))
            temp=dict()
            temp['date']=sold_dates_sales[i]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['net_eft']=eft_added['eft_added']-eft_loss['eft_loss']
            sales_dates.append(temp)

        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            gross_speed= round(gross_sale['sales']/completed_days,0)
            gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
            gross_gap=gross_target['gross_target']-gross_sale['sales']
            gross_speed_required= round(gross_gap/operating_days,0)
            gross_speed_increase = round(100*(gross_speed_required/gross_speed-1),2)

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            cash_speed= round(cash['cash']/completed_days,0)
            cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
            cash_gap=cash_target['cash_target']-cash['cash']
            cash_speed_required= round(cash_gap/operating_days,0)
            cash_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)

            eft_added = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft_loss=Sum('eft_loss'))
            net_eft=eft_added['eft_added']-eft_loss['eft_loss']
            net_eft_speed= round(net_eft/completed_days,0)
            net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
            net_eft_gap=net_eft_target['net_eft_target']-net_eft
            net_eft_speed_required= round(net_eft_gap/operating_days,0)
            net_eft_speed_increase = round(100*(net_eft_speed_required/net_eft_speed-1),2)

            program = sales_filtered.filter(sold_by=trainer[i]).aggregate(program=Count('program_sold'))
            program_speed= round(program['program']/completed_days,0)
            program_target=Target_type.objects.filter(id=5).aggregate(program_target=Sum('monthly_goal'))
            program_gap=program_target['program_target']-program['program']
            program_speed_required= round(program_gap/operating_days,2)
            program_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)


            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross_speed']=gross_speed
            temp['gross_gap']=gross_gap
            temp['gross_speed_required']=gross_speed_required
            temp['gross_speed_increase']=gross_speed_increase

            temp['cash_speed']=cash_speed
            temp['cash_gap']=cash_gap
            temp['cash_speed_required']=cash_speed_required
            temp['cash_speed_increase']=cash_speed_increase

            temp['net_eft_speed']=net_eft_speed
            temp['net_eft_gap']=net_eft_gap
            temp['net_eft_speed_required']=net_eft_speed_required
            temp['net_eft_speed_increase']=net_eft_speed_increase

            temp['program_speed']=program_speed
            temp['program_gap']=program_gap
            temp['program_speed_required']=program_speed_required
            temp['program_speed_increase']=program_speed_increase

            sales_trainer.append(temp)

        print(sales_trainer)
        print(sales_dates)
        print(sales_sum)

        return render(request, 'templates/index.html', {'sales_dates': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                              'sales_trainer': sales_trainer,'sales_sum': sales_sum
                                                        })

    else:
        return render(request, 'base.html', {})

def add_client(request):

    if request.user.is_authenticated():
        form = ClientForm(request.POST or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()


        context = {
        "form": form
        }


        return render(request, 'templates/form_client.html', context)

    else:
        return render(request, 'base.html',{})

def client_table(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_lead=[]
        sales_trainer=[]
        sales_client=[]
        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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

        Client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)

        lead=Client_filtered.values_list('lead_source', flat=True).distinct().order_by('lead_source')
        for i in range(len(lead)):
            gross_sale = Client_filtered.filter(lead_source=lead[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(lead_source=lead[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(lead_source=lead[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['lead']=Lead.objects.filter(id=lead[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_lead.append(temp)

        trainer=Client_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = Client_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_trainer.append(temp)

        client_list=Client_filtered.values_list('client_name', flat=True).distinct().order_by('client_name')
        for i in range(len(client_list)):
            client_name = client_list[i]
            print(client_name)
            gross_sale = Client_filtered.filter(client_name=client_list[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(client_name=client_list[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(client_name=client_list[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['client']=client_name
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_client.append(temp)

        return render(request, 'templates/table_client.html', {'sales_lead': sales_lead,'sales_trainer': sales_trainer, 'sales_client': sales_client,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

def chart(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_lead=[]
        sales_trainer=[]
        sales_client=[]
        sales_program=[]

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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

        Client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)

        lead=Client_filtered.values_list('lead_source', flat=True).distinct().order_by('lead_source')
        for i in range(len(lead)):
            gross_sale = Client_filtered.filter(lead_source=lead[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(lead_source=lead[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(lead_source=lead[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['lead']=Lead.objects.filter(id=lead[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_lead.append(temp)

        trainer=Client_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        for i in range(len(trainer)):
            gross_sale = Client_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_trainer.append(temp)

        client_list=Client_filtered.values_list('client_name', flat=True).distinct().order_by('client_name')
        for i in range(len(client_list)):
            client_name = client_list[i]
            gross_sale = Client_filtered.filter(client_name=client_list[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(client_name=client_list[i]).aggregate(cash=Sum('cash_recieved'))
            eft = Client_filtered.filter(client_name=client_list[i]).aggregate(eft=Sum('eft_added'))

            temp=dict()
            temp['client']=client_name
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft']=eft
            sales_client.append(temp)

        program=Client_filtered.values_list('program_sold', flat=True).distinct().order_by('program_sold')
        total_gross_sale = Client_filtered.all().aggregate(sales=Sum('gross_sale'))
        for i in range(len(program)):
            gross_sale = Client_filtered.filter(program_sold=program[i]).aggregate(share=Sum('gross_sale'))
            share=round(gross_sale.get('share')*100/total_gross_sale.get("sales"))
            temp=dict()
            temp['program']=Program.objects.filter(id=program[i]).values_list('name')[0][0]
            temp['gross']=share
            sales_program.append(temp)

        print(sales_program)
        print(sales_client)
        return render(request, 'templates/client_chart.html', {'sales_lead': sales_lead,'sales_trainer': sales_trainer,
                                                               'sales_client': sales_client,'sales_program': sales_program,
                                                               'reporting_date': repoting_date.strftime("%B, %y"),
                                                               'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})


