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
from appointment.models import appointment
from target.models import Target_type,Goal
from django.db.models import Avg, Max, Min,F, FloatField, Sum,Count
import datetime
import calendar

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
        sales_period=[]
        sales_dates=[]
        lead_info = []
        lead_info_1 = []
        lead_info_2 = []

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        program_dates=client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        gross_period_1 = float()
        gross_period_2 = float()
        cash_period_1 = float()
        cash_period_2 = float()
        net_eft_period_1 = float()
        net_eft_period_2 = float()

        for j in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[j]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[j]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[j]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[j]).aggregate(eft_loss=Sum('eft_loss'))
            if sold_dates[j].day<=15:
                gross_period_1 = gross_period_1+gross_sale['sales']
                cash_period_1=cash_period_1+cash['cash']
                net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
            else:
                gross_period_2=gross_period_2+gross_sale['sales']
                cash_period_2=cash_period_2+cash['cash']
                net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']

        gross_sale = sales_filtered.aggregate(sales=Sum('gross_sale'))
        cash = sales_filtered.aggregate(cash=Sum('cash_recieved'))
        eft_added = sales_filtered.aggregate(eft_added=Sum('eft_added'))
        eft_loss = sales_filtered.aggregate(eft_loss=Sum('eft_loss'))

        temp=dict()
        temp['gross'] = gross_sale
        temp['gross_period_1'] = gross_period_1
        temp['gross_period_2'] = gross_period_2
        temp['cash'] = cash
        temp['cash_period_1'] = cash_period_1
        temp['cash_period_2'] = cash_period_2
        temp['net_eft'] = eft_added['eft_added']-eft_loss['eft_loss']
        temp['net_eft_period_1']=net_eft_period_1
        temp['net_eft_period_2']=net_eft_period_2

        sales_period.append(temp)

        for j in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[j]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[j]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[j]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[j]).aggregate(eft_loss=Sum('eft_loss'))

            temp=dict()
            temp['date'] = sold_dates[j]
            temp['gross'] = gross_sale
            temp['cash'] = cash
            temp['net_eft'] = eft_added['eft_added']-eft_loss['eft_loss']
            sales_dates.append(temp)


        Client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        lead_list=Client_filtered.values_list('lead_source_id', flat=True).distinct().order_by('lead_source_id')

        client_filtered_1=Client_filtered.filter(date_sign_up__lte=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0))
        lead_list_1=client_filtered_1.values_list('lead_source_id', flat=True).distinct().order_by('lead_source_id')

        client_filtered_2=Client_filtered.filter(date_sign_up__gt=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0))
        lead_list_2=client_filtered_2.values_list('lead_source_id', flat=True).distinct().order_by('lead_source_id')

        client_date=Client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        for i in range(len(lead_list)):
            lead = Lead.objects.filter(id=lead_list[i]).values_list('name')[0][0]
            gross_sale = Client_filtered.filter(lead_source_id=lead_list[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(lead_source_id=lead_list[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = Client_filtered.filter(lead_source_id=lead_list[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = Client_filtered.filter(lead_source_id=lead_list[i]).aggregate(eft_loss=Sum('eft_loss'))

            temp=dict()
            temp['lead']=lead
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            lead_info.append(temp)

        for i in range(len(lead_list_1)):
            lead = Lead.objects.filter(id=lead_list_1[i]).values_list('name')[0][0]
            gross_sale = client_filtered_1.filter(lead_source_id=lead_list_1[i]).aggregate(sales=Sum('gross_sale'))
            cash = client_filtered_1.filter(lead_source_id=lead_list_1[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = client_filtered_1.filter(lead_source_id=lead_list_1[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = client_filtered_1.filter(lead_source_id=lead_list_1[i]).aggregate(eft_loss=Sum('eft_loss'))

            temp=dict()
            temp['lead']=lead
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            lead_info_1.append(temp)

        for i in range(len(lead_list_2)):
            lead = Lead.objects.filter(id=lead_list_2[i]).values_list('name')[0][0]
            gross_sale = client_filtered_2.filter(lead_source_id=lead_list_2[i]).aggregate(sales=Sum('gross_sale'))
            cash = client_filtered_2.filter(lead_source_id=lead_list_2[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = client_filtered_2.filter(lead_source_id=lead_list_2[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = client_filtered_2.filter(lead_source_id=lead_list_2[i]).aggregate(eft_loss=Sum('eft_loss'))

            temp=dict()
            temp['lead']=lead
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            lead_info_2.append(temp)
            print(lead_info_2)




        return render(request, 'templates/table_sales.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'list_of_slicer': list_of_slicer,
                                                                  'sales_period': sales_period,
                                                              'lead_info': lead_info,
                                                              'lead_info_1': lead_info_1,
                                                              'lead_info_2': lead_info_2
                                                            })


    else:
        return render(request, 'base.html', {})


def sales_chart_info(request):

    if request.user.is_authenticated():

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})


def sales_kpi(request):

    if request.user.is_authenticated():

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
        appointment_info = []
        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        program_dates=client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        gross_period_1 = float()
        gross_period_2 = float()
        cash_period_1 = float()
        cash_period_2 = float()
        net_eft_period_1 = float()
        net_eft_period_2 = float()
        program_period_1 = float()
        program_period_2 = float()

        for i in range(len(trainer)):
            for j in range(len(sold_dates)):
                gross_sale = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
                if gross_sale['sales'] is None:
                    gross_sale['sales']=0
                else:
                    print('')
                cash = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
                if cash['cash'] is None:
                    cash['cash']=0
                else:
                    print('')

                eft_added = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(eft_added=Sum('eft_added'))
                if eft_added['eft_added'] is None:
                    eft_added['eft_added']=0
                else:
                    print('')

                eft_loss = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(eft_loss=Sum('eft_loss'))
                if eft_loss['eft_loss'] is None:
                    eft_loss['eft_loss']=0
                else:
                    print('')
                if sold_dates[j].day<=15:
                    gross_period_1 = gross_period_1+gross_sale['sales']
                    cash_period_1=cash_period_1+cash['cash']
                    net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
                else:
                    gross_period_2=gross_period_2+gross_sale['sales']
                    cash_period_2=cash_period_2+cash['cash']
                    net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']
            for k in range(len(program_dates)):
                program = client_filtered.filter(date_sign_up=program_dates[k],sold_by=trainer[i]).aggregate(program=Count('program_sold'))

                if program_dates[k].day<=15:
                    program_period_1 = program_period_1+program['program']
                else:
                    program_period_2 = program_period_2+program['program']

            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
            gross_target_1 = Target_type.objects.filter(id=6).aggregate(gross_target_1=Sum('note1'))
            gross_target_2 = Target_type.objects.filter(id=6).aggregate(gross_target_2=Sum('note2'))

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
            cash_target_1 = Target_type.objects.filter(id=7).aggregate(cash_target_1=Sum('note1'))
            cash_target_2 = Target_type.objects.filter(id=7).aggregate(cash_target_2=Sum('note2'))

            eft_added = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_added'))
            eft_loss = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_loss'))
            net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
            net_eft_target_1 = Target_type.objects.filter(id=8).aggregate(net_eft_target_1=Sum('note1'))
            net_eft_target_2 = Target_type.objects.filter(id=8).aggregate(net_eft_target_2=Sum('note2'))

            program = client_filtered.filter(sold_by=trainer[i]).aggregate(program=Count('program_sold'))
            program_target=Target_type.objects.filter(id=5).aggregate(program_target=Sum('monthly_goal'))
            program_target_1 = Target_type.objects.filter(id=5).aggregate(program_target_1=Sum('note1'))
            program_target_2 = Target_type.objects.filter(id=5).aggregate(program_target_2=Sum('note2'))

            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['gross_period_1']=gross_period_1
            temp['gross_period_2']=gross_period_2
            temp['gross_target']=gross_target
            temp['gross_target_1']=gross_target_1
            temp['gross_target_2']=gross_target_2
            temp['gross_kpi']=round(gross_sale['sales']*100/gross_target['gross_target'],0)
            temp['gross_kpi_1']=round(gross_period_1*100/gross_target_1['gross_target_1'],0)
            temp['gross_kpi_2']=round(gross_period_2*100/gross_target_2['gross_target_2'],0)

            temp['cash']=cash
            temp['cash_period_1']=cash_period_1
            temp['cash_period_2']=cash_period_2
            temp['cash_target']=cash_target
            temp['cash_target_1'] = cash_target_1
            temp['cash_target_2'] = cash_target_2
            temp['cash_kpi']=round(cash['cash']*100/cash_target['cash_target'],0)
            temp['cash_kpi_1']=round(cash_period_1*100/cash_target_1['cash_target_1'],0)
            temp['cash_kpi_2']=round(cash_period_2*100/cash_target_2['cash_target_2'],0)

            temp['net_eft']=eft_added['eft']-eft_loss['eft']
            temp['net_eft_period_1']=net_eft_period_1
            temp['net_eft_period_2']=net_eft_period_2
            temp['net_eft_target']=net_eft_target
            temp['net_eft_target_1']=net_eft_target_1
            temp['net_eft_target_2']=net_eft_target_2
            temp['net_eft_kpi']=round((eft_added['eft']-eft_loss['eft'])*100/net_eft_target['net_eft_target'],0)
            temp['net_eft_kpi_1']=round(net_eft_period_1*100/net_eft_target_1['net_eft_target_1'],0)
            temp['net_eft_kpi_2']=round(net_eft_period_2*100/net_eft_target_2['net_eft_target_2'],0)

            temp['program']=program
            temp['program_1']=program_period_1
            temp['program_2']=program_period_2
            temp['program_target']=program_target
            temp['program_target_1']=program_target_1
            temp['program_target_2']=program_target_2

            temp['program_kpi']=round(program['program']*100/program_target['program_target'],0)
            temp['program_kpi_1']=round(program_period_1*100/program_target_1['program_target_1'],0)
            temp['program_kpi_2']=round(program_period_2*100/program_target_2['program_target_2'],0)

            sales_trainer.append(temp)


        appointment_filtered=appointment.objects.filter(date__month=slicer2,date__year=slicer1)
        client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        admin_staff=appointment_filtered.values_list('input_by', flat=True).distinct().order_by('input_by')
        appointment_dates=appointment_filtered.values_list('date', flat=True).distinct().order_by('-date')
        requests_period_1 =int()
        requests_period_2 =int()
        scheduled_period_1 =int()
        scheduled_period_2 =int()
        attended_period_1 =int()
        attended_period_2 =int()

        for i in range(len(admin_staff)):
            for j in range(len(appointment_dates)):
                requests = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(requests=Sum('consultations_requested'))
                scheduled = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(scheduled=Sum('consultations_scheduled'))
                attended = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(attended=Sum('consultations_attended'))

                if requests['requests'] is None:
                    requests['requests']=0
                else:
                    print('')


                if scheduled['scheduled'] is None:
                    scheduled['scheduled']=0
                else:
                    print('')

                if attended['attended'] is None:
                    attended['attended']=0
                else:
                    print('')

                if appointment_dates[j].day<=15:
                    requests_period_1 = requests_period_1+requests['requests']
                    scheduled_period_1=scheduled_period_1+scheduled['scheduled']
                    attended_period_1=attended_period_1+attended['attended']
                else:
                    requests_period_2 = requests_period_2 + requests['requests']
                    scheduled_period_2 = scheduled_period_2 + scheduled['scheduled']
                    attended_period_2 = attended_period_2 + attended['attended']

            requests = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(requests=Sum('consultations_requested'))
            requests_target=Target_type.objects.filter(id=2).aggregate(requests_target=Sum('monthly_goal'))
            requests_target_1=Target_type.objects.filter(id=2).aggregate(requests_target_1=Sum('note1'))
            requests_target_2=Target_type.objects.filter(id=2).aggregate(requests_target_2=Sum('note2'))

            scheduled = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(scheduled=Sum('consultations_scheduled'))
            scheduled_target = Target_type.objects.filter(id=3).aggregate(scheduled_target=Sum('monthly_goal'))
            scheduled_target_1 = Target_type.objects.filter(id=3).aggregate(scheduled_target_1=Sum('note1'))
            scheduled_target_2 = Target_type.objects.filter(id=3).aggregate(scheduled_target_2=Sum('note2'))


            attended = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(attended=Sum('consultations_attended'))
            attended_target = Target_type.objects.filter(id=4).aggregate(attended_target=Sum('monthly_goal'))
            attended_target_1 = Target_type.objects.filter(id=4).aggregate(attended_target_1=Sum('note1'))
            attended_target_2 = Target_type.objects.filter(id=4).aggregate(attended_target_2=Sum('note2'))

            temp=dict()
            print(admin_staff)
            print(Trainer.objects.filter(id=admin_staff[0]).values_list('name'))

            temp['person']=Trainer.objects.filter(id=admin_staff[i]).values_list('name')[0][0]
            temp['requests']=requests
            temp['requests_period_1']= requests_period_1
            temp['requests_period_2']= requests_period_2
            temp['requests_target']= requests_target
            temp['requests_target_1']= requests_target_1
            temp['requests_target_2']=requests_target_2
            temp['requests_kpi']=round(requests['requests']*100/requests_target['requests_target'],0)
            temp['requests_kpi_1']=round(requests_period_1*100/requests_target_1['requests_target_1'],0)
            temp['requests_kpi_2']=round(requests_period_2*100/requests_target_2['requests_target_2'],0)

            temp['scheduled']=scheduled
            temp['scheduled_period_1']=scheduled_period_1
            temp['scheduled_period_2']=scheduled_period_2
            temp['scheduled_target']=scheduled_target
            temp['scheduled_target_1'] = scheduled_target_1
            temp['scheduled_target_2'] = scheduled_target_2
            temp['scheduled_kpi']=round(scheduled['scheduled']*100/scheduled_target['scheduled_target'],0)
            temp['scheduled_kpi_1']=round(scheduled_period_1*100/scheduled_target_1['scheduled_target_1'],0)
            temp['scheduled_kpi_2']=round(scheduled_period_2*100/scheduled_target_2['scheduled_target_2'],0)


            temp['attended']=attended
            temp['attended_period_1'] = attended_period_1
            temp['attended_period_2'] = attended_period_2
            temp['attended_target'] = attended_target
            temp['attended_target_1'] = attended_target_1
            temp['attended_target_2'] = attended_target_2
            temp['attended_kpi']=round(attended['attended']*100/attended_target['attended_target'],0)
            temp['attended_kpi_1']=round(attended_period_1*100/attended_target_1['attended_target_1'],0)
            temp['attended_kpi_2']=round(attended_period_2*100/attended_target_2['attended_target_2'],0)

            appointment_info.append(temp)



        return render(request, 'templates/table_kpi.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'list_of_slicer': list_of_slicer,
                                                                  'trainer': sales_trainer,
                                                            'appointment': appointment_info})

    else:
        return render(request, 'base.html', {})


def sales_kpi_chart_info(request):

    if request.user.is_authenticated():

        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_dates=[]
        appointment_info = []
        months = Record.objects.values_list('date',flat=True).distinct().order_by('-date')
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
        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)
        client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        trainer=sales_filtered.values_list('sold_by', flat=True).distinct().order_by('sold_by')
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        program_dates=client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        gross_period_1 = float()
        gross_period_2 = float()
        cash_period_1 = float()
        cash_period_2 = float()
        net_eft_period_1 = float()
        net_eft_period_2 = float()
        program_period_1 = float()
        program_period_2 = float()

        for i in range(len(trainer)):
            print(trainer)
            for j in range(len(sold_dates)):
                gross_sale = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
                cash = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
                eft_added = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(eft_added=Sum('eft_added'))
                eft_loss = sales_filtered.filter(date=sold_dates[j],sold_by=trainer[i]).aggregate(eft_loss=Sum('eft_loss'))

                if gross_sale['sales'] is None:
                    gross_sale['sales']=0
                else:
                    print('')
                if cash['cash'] is None:
                    cash['cash']=0
                else:
                    print('')

                if eft_added['eft_added'] is None:
                    eft_added['eft_added']=0
                else:
                    print('')

                if eft_loss['eft_loss'] is None:
                    eft_loss['eft_loss']=0
                else:
                    print('')
                if sold_dates[j].day<=15:
                    gross_period_1 = gross_period_1+gross_sale['sales']
                    cash_period_1=cash_period_1+cash['cash']
                    net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
                else:
                    gross_period_2=gross_period_2+gross_sale['sales']
                    cash_period_2=cash_period_2+cash['cash']
                    net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']

                print(gross_period_1)
                print(gross_period_2)
            for k in range(len(program_dates)):
                program = client_filtered.filter(date_sign_up=program_dates[k],sold_by=trainer[i]).aggregate(program=Count('program_sold'))

                if program_dates[k].day<=15:
                    program_period_1 = program_period_1+program['program']
                else:
                    program_period_2 = program_period_2+program['program']

            gross_sale = sales_filtered.filter(sold_by=trainer[i]).aggregate(sales=Sum('gross_sale'))
            gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
            gross_target_1 = Target_type.objects.filter(id=6).aggregate(gross_target_1=Sum('note1'))
            gross_target_2 = Target_type.objects.filter(id=6).aggregate(gross_target_2=Sum('note2'))

            cash = sales_filtered.filter(sold_by=trainer[i]).aggregate(cash=Sum('cash_recieved'))
            cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
            cash_target_1 = Target_type.objects.filter(id=7).aggregate(cash_target_1=Sum('note1'))
            cash_target_2 = Target_type.objects.filter(id=7).aggregate(cash_target_2=Sum('note2'))

            eft_added = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_added'))
            eft_loss = sales_filtered.filter(sold_by=trainer[i]).aggregate(eft=Sum('eft_loss'))
            net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
            net_eft_target_1 = Target_type.objects.filter(id=8).aggregate(net_eft_target_1=Sum('note1'))
            net_eft_target_2 = Target_type.objects.filter(id=8).aggregate(net_eft_target_2=Sum('note2'))

            program = client_filtered.filter(sold_by=trainer[i]).aggregate(program=Count('program_sold'))
            program_target=Target_type.objects.filter(id=5).aggregate(program_target=Sum('monthly_goal'))
            program_target_1 = Target_type.objects.filter(id=5).aggregate(program_target_1=Sum('note1'))
            program_target_2 = Target_type.objects.filter(id=5).aggregate(program_target_2=Sum('note2'))

            temp=dict()
            temp['trainer']=Trainer.objects.filter(id=trainer[i]).values_list('name')[0][0]
            temp['gross']=gross_sale
            temp['gross_period_1']=gross_period_1
            temp['gross_period_2']=gross_period_2
            temp['gross_target']=gross_target
            temp['gross_target_1']=gross_target_1
            temp['gross_target_2']=gross_target_2
            temp['gross_kpi']=round(gross_sale['sales']*100/gross_target['gross_target'],0)
            temp['gross_kpi_1']=round(gross_period_1*100/gross_target_1['gross_target_1'],0)
            temp['gross_kpi_2']=round(gross_period_2*100/gross_target_2['gross_target_2'],0)

            temp['cash']=cash
            temp['cash_period_1']=cash_period_1
            temp['cash_period_2']=cash_period_2
            temp['cash_target']=cash_target
            temp['cash_target_1'] = cash_target_1
            temp['cash_target_2'] = cash_target_2
            temp['cash_kpi']=round(cash['cash']*100/cash_target['cash_target'],0)
            temp['cash_kpi_1']=round(cash_period_1*100/cash_target_1['cash_target_1'],0)
            temp['cash_kpi_2']=round(cash_period_2*100/cash_target_2['cash_target_2'],0)

            temp['net_eft']=eft_added['eft']-eft_loss['eft']
            temp['net_eft_period_1']=net_eft_period_1
            temp['net_eft_period_2']=net_eft_period_2
            temp['net_eft_target']=net_eft_target
            temp['net_eft_target_1']=net_eft_target_1
            temp['net_eft_target_2']=net_eft_target_2
            temp['net_eft_kpi']=round((eft_added['eft']-eft_loss['eft'])*100/net_eft_target['net_eft_target'],0)
            temp['net_eft_kpi_1']=round(net_eft_period_1*100/net_eft_target_1['net_eft_target_1'],0)
            temp['net_eft_kpi_2']=round(net_eft_period_2*100/net_eft_target_2['net_eft_target_2'],0)

            temp['program']=program
            temp['program_1']=program_period_1
            temp['program_2']=program_period_2
            temp['program_target']=program_target
            temp['program_target_1']=program_target_1
            temp['program_target_2']=program_target_2

            temp['program_kpi']=round(program['program']*100/program_target['program_target'],0)
            temp['program_kpi_1']=round(program_period_1*100/program_target_1['program_target_1'],0)
            temp['program_kpi_2']=round(program_period_2*100/program_target_2['program_target_2'],0)

            sales_trainer.append(temp)


        appointment_filtered=appointment.objects.filter(date__month=slicer2,date__year=slicer1)
        client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        admin_staff=appointment_filtered.values_list('input_by', flat=True).distinct().order_by('input_by')
        print(admin_staff)
        appointment_dates=appointment_filtered.values_list('date', flat=True).distinct().order_by('-date')
        requests_period_1 =int()
        requests_period_2 =int()
        scheduled_period_1 =int()
        scheduled_period_2 =int()
        attended_period_1 =int()
        attended_period_2 =int()

        for i in range(len(admin_staff)):
            for j in range(len(appointment_dates)):
                requests = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(requests=Sum('consultations_requested'))
                scheduled = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(scheduled=Sum('consultations_scheduled'))
                attended = appointment_filtered.filter(input_by=admin_staff[i],date=appointment_dates[j]).aggregate(attended=Sum('consultations_attended'))

                if requests['requests'] is None:
                    requests['requests']=0
                else:
                    print('')


                if scheduled['scheduled'] is None:
                    scheduled['scheduled']=0
                else:
                    print('')

                if attended['attended'] is None:
                    attended['attended']=0
                else:
                    print('')

                if appointment_dates[j].day<=15:
                    requests_period_1 = requests_period_1+requests['requests']
                    scheduled_period_1=scheduled_period_1+scheduled['scheduled']
                    attended_period_1=attended_period_1+attended['attended']
                else:
                    requests_period_2 = requests_period_2 + requests['requests']
                    scheduled_period_2 = scheduled_period_2 + scheduled['scheduled']
                    attended_period_2 = attended_period_2 + attended['attended']

            requests = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(requests=Sum('consultations_requested'))
            requests_target=Target_type.objects.filter(id=2).aggregate(requests_target=Sum('monthly_goal'))
            requests_target_1=Target_type.objects.filter(id=2).aggregate(requests_target_1=Sum('note1'))
            requests_target_2=Target_type.objects.filter(id=2).aggregate(requests_target_2=Sum('note2'))

            scheduled = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(scheduled=Sum('consultations_scheduled'))
            scheduled_target = Target_type.objects.filter(id=3).aggregate(scheduled_target=Sum('monthly_goal'))
            scheduled_target_1 = Target_type.objects.filter(id=3).aggregate(scheduled_target_1=Sum('note1'))
            scheduled_target_2 = Target_type.objects.filter(id=3).aggregate(scheduled_target_2=Sum('note2'))


            attended = appointment_filtered.filter(input_by=admin_staff[i]).aggregate(attended=Sum('consultations_attended'))
            attended_target = Target_type.objects.filter(id=4).aggregate(attended_target=Sum('monthly_goal'))
            attended_target_1 = Target_type.objects.filter(id=4).aggregate(attended_target_1=Sum('note1'))
            attended_target_2 = Target_type.objects.filter(id=4).aggregate(attended_target_2=Sum('note2'))

            temp=dict()
            print(Trainer.objects.filter(id=admin_staff[i]).values_list('name')[0][0])
            temp['person']=Trainer.objects.filter(id=admin_staff[i]).values_list('name')[0][0]
            temp['requests']=requests
            temp['requests_period_1']= requests_period_1
            temp['requests_period_2']= requests_period_2
            temp['requests_target']= requests_target
            temp['requests_target_1']= requests_target_1
            temp['requests_target_2']=requests_target_2
            temp['requests_kpi']=round(requests['requests']*100/requests_target['requests_target'],0)
            temp['requests_kpi_1']=round(requests_period_1*100/requests_target_1['requests_target_1'],0)
            temp['requests_kpi_2']=round(requests_period_2*100/requests_target_2['requests_target_2'],0)

            temp['scheduled']=scheduled
            temp['scheduled_period_1']=scheduled_period_1
            temp['scheduled_period_2']=scheduled_period_2
            temp['scheduled_target']=scheduled_target
            temp['scheduled_target_1'] = scheduled_target_1
            temp['scheduled_target_2'] = scheduled_target_2
            temp['scheduled_kpi']=round(scheduled['scheduled']*100/scheduled_target['scheduled_target'],0)
            temp['scheduled_kpi_1']=round(scheduled_period_1*100/scheduled_target_1['scheduled_target_1'],0)
            temp['scheduled_kpi_2']=round(scheduled_period_2*100/scheduled_target_2['scheduled_target_2'],0)


            temp['attended']=attended
            temp['attended_period_1'] = attended_period_1
            temp['attended_period_2'] = attended_period_2
            temp['attended_target'] = attended_target
            temp['attended_target_1'] = attended_target_1
            temp['attended_target_2'] = attended_target_2
            temp['attended_kpi']=round(attended['attended']*100/attended_target['attended_target'],0)
            temp['attended_kpi_1']=round(attended_period_1*100/attended_target_1['attended_target_1'],0)
            temp['attended_kpi_2']=round(attended_period_2*100/attended_target_2['attended_target_2'],0)

            appointment_info.append(temp)

        print(sales_trainer)
        print(appointment_info)

        return render(request, 'templates/sales_kpi_chart.html', {'sales_date': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'list_of_slicer': list_of_slicer,
                                                                  'trainer': sales_trainer,
                                                            'appointment': appointment_info})

    else:
        return render(request, 'base.html', {})


def sales_current_kpi_table(request):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_sum=[]
        sales_dates=[]
        sales_period=[]

        repoting_date = datetime.datetime.now()
        sales_filtered=Record.objects.filter(date__month=repoting_date.month,date__year=repoting_date.year)
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        client_filtered=Client.objects.filter(date_sign_up__month=repoting_date.month,date_sign_up__year=repoting_date.year)
        appointment_filtered=appointment.objects.filter(date__month=repoting_date.month,date__year=repoting_date.year)
        appointment_dates=appointment_filtered.values_list('date', flat=True).distinct().order_by('-date')


        max_days=calendar.monthrange(repoting_date.year,repoting_date.month)[1]
        completed_days=repoting_date.day
        operating_days=max_days-completed_days

        completed_days_1=min(15,completed_days)
        completed_days_2=completed_days-completed_days_1

        operating_days_2=min(max_days-completed_days,max_days-15)
        operating_days_1=operating_days-operating_days_2

        gross_period_1 =float()
        gross_period_2 =float()
        cash_period_1 =float()
        cash_period_2 =float()
        net_eft_period_1 =float()
        net_eft_period_2 =float()
        requests_period_1 =int()
        requests_period_2 =int()
        scheduled_period_1 =int()
        scheduled_period_2 =int()
        attended_period_1 =int()
        attended_period_2 =int()
        closed_period_1 =int()
        closed_period_2 =int()




        try:
            for i in range(len(sold_dates)):
                gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
                cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
                eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
                eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))

                if sold_dates[i].day<=15:
                    gross_period_1 = gross_period_1+gross_sale['sales']
                    cash_period_1=cash_period_1+cash['cash']
                    net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
                else:
                    gross_period_2=gross_period_2+gross_sale['sales']
                    cash_period_2=cash_period_2+cash['cash']
                    net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']

            for i in range(len(appointment_dates)):
                requests = appointment_filtered.filter(date=appointment_dates[i]).aggregate(requests=Sum('consultations_requested'))
                scheduled = appointment_filtered.filter(date=appointment_dates[i]).aggregate(scheduled=Sum('consultations_scheduled'))
                closed = appointment_filtered.filter(date=appointment_dates[i]).aggregate(closed=Sum('consultations_closed'))
                attended = appointment_filtered.filter(date=appointment_dates[i]).aggregate(attended=Sum('consultations_attended'))
                if appointment_dates[i].day<=15:
                    requests_period_1 = requests_period_1+requests['requests']
                    scheduled_period_1= scheduled_period_1 + scheduled['scheduled']
                    closed_period_1 = closed_period_1 + closed['closed']
                    attended_period_1 = attended_period_1 + attended['attended']
                else:
                    requests_period_2 = requests_period_2+requests['requests']
                    scheduled_period_2= scheduled_period_2 + scheduled['scheduled']
                    closed_period_2 = closed_period_2 + closed['closed']
                    attended_period_2 = attended_period_2 + attended['attended']

            gross_sale = sales_filtered.aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.aggregate(eft_loss=Sum('eft_loss'))
            net_eft=eft_added['eft_added']-eft_loss['eft_loss']
            requests = appointment_filtered.aggregate(requests=Sum('consultations_requested'))
            scheduled = appointment_filtered.aggregate(scheduled=Sum('consultations_scheduled'))
            attended = appointment_filtered.aggregate(attended=Sum('consultations_attended'))
            closed = appointment_filtered.aggregate(closed=Sum('consultations_closed'))


            gross_speed= int(gross_sale['sales']/completed_days)
            cash_speed= round(cash['cash']/completed_days,0)
            net_eft_speed= round(net_eft/completed_days,0)
            requests_speed= round(requests['requests']/completed_days,1)
            scheduled_speed= round(scheduled['scheduled']/completed_days,1)
            attended_speed= round(attended['attended']/completed_days,1)
            closed_speed= round(closed['closed']/completed_days,1)

            if completed_days_1 !=0:
                gross_speed_1 = round(gross_period_1/completed_days_1,0)
                cash_speed_1 = round(cash_period_1/completed_days_1,0)
                net_eft_speed_1 = round(net_eft_period_1/completed_days_1,0)
                requests_speed_1 = round(requests_period_1/completed_days_1,0)
                scheduled_speed_1 = round(scheduled_period_1/completed_days_1,0)
                attended_speed_1 = round(attended_period_1/completed_days_1,0)
                closed_speed_1 = round(closed_period_1/completed_days_1,0)

            else:
                gross_speed_1="Period Not Started"
                cash_speed_1="Period Not Started"
                net_eft_speed_1 = "Period Not Started"
                requests_speed_1 = "Period Not Started"
                scheduled_speed_1 = "Period Not Started"
                attended_speed_1 = "Period Not Started"
                closed_speed_1 = "Period Not Started"

            if completed_days_2 !=0:
                gross_speed_2=int(gross_period_2/completed_days_2)
                cash_speed_2 = round(cash_period_2/completed_days_2,0)
                net_eft_speed_2 = round(net_eft_period_2/completed_days_2,0)
                requests_speed_2 = round(requests_period_2/completed_days_2,0)
                scheduled_speed_2 = round(scheduled_period_2/completed_days_2,0)
                attended_speed_2 = round(attended_period_2/completed_days_2,0)
                closed_speed_2 = round(closed_period_2/completed_days_2,0)

            else:
                gross_speed_2='Period Not Started'
                cash_speed_2 = round(cash_period_2/completed_days_2,0)
                net_eft_speed_2 = round(net_eft_period_2/completed_days_2,0)
                requests_speed_2 = "Period Not Started"
                scheduled_speed_2 = "Period Not Started"
                attended_speed_2 = "Period Not Started"
                closed_speed_2 = "Period Not Started"

            gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
            cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
            net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
            scheduled_target=Target_type.objects.filter(id=3).aggregate(scheduled_target=Sum('monthly_goal'))
            requests_target=Target_type.objects.filter(id=2).aggregate(requests_target=Sum('monthly_goal'))
            attended_target=Target_type.objects.filter(id=4).aggregate(attended_target=Sum('monthly_goal'))



            gross_target_1 = Target_type.objects.filter(id=6).aggregate(gross_target_1=Sum('note1'))
            gross_target_2 = Target_type.objects.filter(id=6).aggregate(gross_target_2=Sum('note2'))
            cash_target_1 = Target_type.objects.filter(id=7).aggregate(cash_target_1=Sum('note1'))
            cash_target_2 = Target_type.objects.filter(id=7).aggregate(cash_target_2=Sum('note2'))
            net_eft_target_1 = Target_type.objects.filter(id=8).aggregate(net_eft_target_1=Sum('note1'))
            net_eft_target_2 = Target_type.objects.filter(id=8).aggregate(net_eft_target_2=Sum('note2'))
            requests_target_1 = Target_type.objects.filter(id=2).aggregate(requests_target_1=Sum('note1'))
            requests_target_2 = Target_type.objects.filter(id=2).aggregate(requests_target_2=Sum('note2'))
            scheduled_target_1 = Target_type.objects.filter(id=3).aggregate(scheduled_target_1=Sum('note1'))
            scheduled_target_2 = Target_type.objects.filter(id=3).aggregate(scheduled_target_2=Sum('note2'))
            attended_target_1 = Target_type.objects.filter(id=4).aggregate(attended_target_1=Sum('note1'))
            attended_target_2 = Target_type.objects.filter(id=4).aggregate(attended_target_2=Sum('note2'))


            gross_gap=gross_target['gross_target']-gross_sale['sales']
            cash_gap=cash_target['cash_target']-cash['cash']
            net_eft_gap=net_eft_target['net_eft_target']-net_eft
            requests_gap=requests_target['requests_target']-requests['requests']
            scheduled_gap=scheduled_target['scheduled_target']-scheduled['scheduled']
            attended_gap=attended_target['attended_target']-attended['attended']

            gross_gap_1=gross_target_1['gross_target_1']-gross_period_1
            gross_gap_2=gross_target_2['gross_target_2']-gross_period_2
            cash_gap_1=cash_target_1['cash_target_1']-cash_period_1
            cash_gap_2=cash_target_2['cash_target_2']-cash_period_2
            net_eft_gap_1=net_eft_target_1['net_eft_target_1']-net_eft_period_1
            net_eft_gap_2=net_eft_target_2['net_eft_target_2']-net_eft_period_2
            requests_gap_1=requests_target_1['requests_target_1']-requests_period_1
            requests_gap_2=requests_target_2['requests_target_2']-requests_period_2
            scheduled_gap_1=scheduled_target_1['scheduled_target_1']-scheduled_period_1
            scheduled_gap_2=scheduled_target_2['scheduled_target_2']-scheduled_period_2
            attended_gap_1=attended_target_1['attended_target_1']-attended_period_1
            attended_gap_2=attended_target_2['attended_target_2']-attended_period_2

            if operating_days > 0:
                gross_speed_required= round(gross_gap/operating_days,1)
                if gross_speed >0:
                    gross_speed_increase = round(100*(gross_speed_required/gross_speed-1),2)
                else:
                    gross_speed_increase = "N/A"
                cash_speed_required= round(cash_gap/operating_days,1)
                if cash_speed > 0:
                    cash_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)
                else:
                    cash_speed_increase = "N/A"
                net_eft_speed_required= round(net_eft_gap/operating_days,1)
                if net_eft_speed >0:
                    net_eft_speed_increase = round(100*(net_eft_speed_required/net_eft_speed-1),2)
                else:
                    net_eft_speed_increase = 'N/A'
                requests_speed_required= round(requests_gap/operating_days,1)
                if requests_speed >0:
                    requests_speed_increase = round(100*(requests_speed_required/requests_speed-1),2)
                else:
                    requests_speed_increase = 'N/A'
                scheduled_speed_required= round(scheduled_gap/operating_days,1)
                if scheduled_speed >0:
                    scheduled_speed_increase = round(100*(scheduled_speed_required/scheduled_speed-1),2)
                else:
                    scheduled_speed_increase = 'N/A'
                attended_speed_required= round(requests_gap/operating_days,1)
                if attended_speed >0:
                    attended_speed_increase = round(100*(attended_speed_required/attended_speed-1),2)
                else:
                    attended_speed_increase = 'N/A'

            else:
                gross_speed_required="No operating days"
                gross_speed_increase = "No Operating days"
                cash_speed_required="No operating days"
                cash_speed_increase = "No Operating days"
                net_eft_speed_required="No operating days"
                net_eft_speed_increase = "No Operating days"
                requests_speed_required="No operating days"
                requests_speed_increase = "No Operating days"
                scheduled_speed_required="No operating days"
                scheduled_speed_increase = "No Operating days"
                attended_speed_required="No operating days"
                attended_speed_increase = "No Operating days"

            if operating_days_1 > 0:
                gross_speed_required_1= round(gross_gap_1/operating_days_1,1)
                if type(gross_speed_1)==str or gross_speed_1==0:
                    gross_speed_increase_1 = "N/A"
                else:
                    gross_speed_increase_1 = round(100*(gross_speed_required_1/gross_speed_1-1),2)

                cash_speed_required_1= round(cash_gap_1/operating_days_1,1)
                if type(cash_speed_1)==str or cash_speed_1==0:
                    cash_speed_increase_1='N/A'
                else:
                    cash_speed_increase_1 = round(100*(cash_speed_required_1/cash_speed_1-1),2)

                net_eft_speed_required_1= round(net_eft_gap_1/operating_days_1,1)
                if type(net_eft_speed_1)== str or net_eft_speed_1 ==0:
                    net_eft_speed_increase_1='N/A'
                else:
                    net_eft_speed_increase_1 = round(100*(net_eft_speed_required_1/net_eft_speed_1-1),2)

                requests_speed_required_1= round(requests_gap_1/operating_days_1,1)
                if type(requests_speed_1)==str or requests_speed_1==0:
                    requests_speed_increase_1='N/A'
                else:
                    requests_speed_increase_1 = round(100*(requests_speed_required_1/requests_speed_1-1),2)

                scheduled_speed_required_1= round(scheduled_gap_1/operating_days_1,1)
                if type(scheduled_speed_1)==str or scheduled_speed_1==0:
                    scheduled_speed_increase_1='N/A'
                else:
                    scheduled_speed_increase_1 = round(100*(scheduled_speed_required_1/scheduled_speed_1-1),2)

                attended_speed_required_1= round(attended_gap_1/operating_days_1,1)
                if type(attended_speed_1)==str or attended_speed_1==0:
                    attended_speed_increase_1='N/A'
                else:
                    attended_speed_increase_1 = round(100*(attended_speed_required_1/attended_speed_1-1),2)


            else:
                gross_speed_required_1 = "Completed Period"
                gross_speed_increase_1 = "Completed Period"
                cash_speed_required_1 = "Completed Period"
                cash_speed_increase_1 = "Completed Period"
                net_eft_speed_required_1 = "Completed Period"
                net_eft_speed_increase_1 = "Completed Period"
                requests_speed_required_1 = "Completed Period"
                requests_speed_increase_1 = "Completed Period"
                scheduled_speed_required_1 = "Completed Period"
                scheduled_speed_increase_1 = "Completed Period"
                attended_speed_required_1 = "Completed Period"
                attended_speed_increase_1 = "Completed Period"

            if operating_days_2 > 0:
                gross_speed_required_2= round(gross_gap_2/operating_days_2,1)
                if type(gross_speed_2)==str or gross_speed_2==0:
                    gross_speed_increase_2 = "N/A"
                else:
                    gross_speed_increase_2 = round(100*(gross_speed_required_2/gross_speed_2-1),2)

                cash_speed_required_2= round(cash_gap_2/operating_days_2,1)
                if type(cash_speed_2)==str or cash_speed_2==0:
                    cash_speed_increase_2='N/A'
                else:
                    cash_speed_increase_2 = round(100*(cash_speed_required_2/cash_speed_2-1),2)

                net_eft_speed_required_2= round(net_eft_gap_2/operating_days_2,1)
                if type(net_eft_speed_2)== str or net_eft_speed_2 ==0:
                    net_eft_speed_increase_2='N/A'
                else:
                    net_eft_speed_increase_2 = round(100*(net_eft_speed_required_2/net_eft_speed_2-1),2)
                requests_speed_required_2= round(requests_gap_2/operating_days_2,1)
                if type(requests_speed_2)==str or requests_speed_2==0:
                    requests_speed_increase_2='N/A'
                else:
                    requests_speed_increase_2 = round(100*(requests_speed_required_2/requests_speed_2-1),2)

                scheduled_speed_required_2= round(scheduled_gap_2/operating_days_2,1)
                if type(scheduled_speed_2)==str or scheduled_speed_2==0:
                    scheduled_speed_increase_2='N/A'
                else:
                    scheduled_speed_increase_2 = round(100*(scheduled_speed_required_2/scheduled_speed_2-1),2)

                attended_speed_required_2= round(attended_gap_2/operating_days_2,1)
                if type(attended_speed_2)==str or attended_speed_2==0:
                    attended_speed_increase_2='N/A'
                else:
                    attended_speed_increase_2 = round(100*(attended_speed_required_1/attended_speed_1-1),2)


            else:
                gross_speed_required_2 = "Completed Period"
                gross_speed_increase_2 = "Completed Period"
                cash_speed_required_2 = "Completed Period"
                cash_speed_increase_2 = "Completed Period"
                net_eft_speed_required_2 = "Completed Period"
                net_eft_speed_increase_2 = "Completed Period"
                requests_speed_required_2 = "Completed Period"
                requests_speed_increase_2 = "Completed Period"
                scheduled_speed_required_2 = "Completed Period"
                scheduled_speed_increase_2 = "Completed Period"
                attended_speed_required_2 = "Completed Period"
                attended_speed_increase_2 = "Completed Period"


            temp0=dict()
            temp0['gross_sale']=int(gross_sale['sales'])
            temp0['gross_period_1']=int(gross_period_1)
            temp0['gross_period_2']=int(gross_period_2)

            temp0['gross_speed']=int(gross_speed)
            temp0['gross_speed_1']=int(gross_speed_1)
            temp0['gross_speed_2']=int(gross_speed_2)

            temp0['gross_gap']=int(gross_gap)
            temp0['gross_gap_1']=int(gross_gap_1)
            temp0['gross_gap_2']=int(gross_gap_2)

            temp0['gross_speed_required']=gross_speed_required
            temp0['gross_speed_required_1']=gross_speed_required_1
            temp0['gross_speed_required_2']=gross_speed_required_2

            temp0['gross_speed_increase']=gross_speed_increase
            temp0['gross_speed_increase_1']=gross_speed_increase_1
            temp0['gross_speed_increase_2']=gross_speed_increase_2

            temp0['cash']=int(cash['cash'])
            temp0['cash_period_1']=int(cash_period_1)
            temp0['cash_period_2']=int(cash_period_2)
            temp0['cash_speed']=cash_speed
            temp0['cash_speed_1']=cash_speed_1
            temp0['cash_speed_2']=cash_speed_2

            temp0['cash_gap']=cash_gap
            temp0['cash_gap_1']=cash_gap_1
            temp0['cash_gap_2']=cash_gap_2

            temp0['cash_speed_required']=cash_speed_required
            temp0['cash_speed_required_1']=cash_speed_required_1
            temp0['cash_speed_required_2']=cash_speed_required_2

            temp0['cash_speed_increase']=cash_speed_increase
            temp0['cash_speed_increase_1']=cash_speed_increase_1
            temp0['cash_speed_increase_2']=cash_speed_increase_2

            temp0['net_eft']=int(net_eft)
            temp0['net_eft_period_1']=int(net_eft_period_1)
            temp0['net_eft_period_2']=int(net_eft_period_2)

            temp0['net_eft_speed']=int(net_eft_speed)
            temp0['net_eft_speed_1']=int(net_eft_speed_1)
            temp0['net_eft_speed_2']=int(net_eft_speed_2)

            temp0['net_eft_gap']=net_eft_gap
            temp0['net_eft_gap_1']=net_eft_gap_1
            temp0['net_eft_gap_2']=net_eft_gap_2

            temp0['net_eft_speed_required']=net_eft_speed_required
            temp0['net_eft_speed_required_1']=net_eft_speed_required_1
            temp0['net_eft_speed_required_2']=net_eft_speed_required_2

            temp0['net_eft_speed_increase']=net_eft_speed_increase
            temp0['net_eft_speed_increase_1']=net_eft_speed_increase_1
            temp0['net_eft_speed_increase_2']=net_eft_speed_increase_2

            temp0['requests']=int(requests['requests'])
            temp0['requests_period_1']=requests_period_1
            temp0['requests_period_2']=requests_period_2

            temp0['requests_speed']=requests_speed
            temp0['requests_speed_1']=requests_speed_1
            temp0['request_speeds_2']=requests_speed_2

            temp0['requests_gap']= requests_gap
            temp0['requests_gap_1']=requests_gap_1
            temp0['requests_gap_2']=requests_gap_2

            temp0['requests_speed_required']= requests_speed_required
            temp0['requests_speed_required_1']= requests_speed_required_1
            temp0['requests_speed_required_2']= requests_speed_required_2

            temp0['requests_speed_increase']= requests_speed_increase
            temp0['requests_speed_increase_1']= requests_speed_increase_1
            temp0['requests_speed_increase_2']= requests_speed_increase_2

            temp0['scheduled']=int(scheduled['scheduled'])
            temp0['scheduled_period_1']=scheduled_period_1
            temp0['scheduled_period_2']=scheduled_period_2

            temp0['scheduled_speed']= scheduled_speed
            temp0['scheduled_speed_1']=scheduled_speed_1
            temp0['scheduled_speed_2']=scheduled_speed_2

            temp0['scheduled_gap']= scheduled_gap
            temp0['scheduled_gap_1']= scheduled_gap_1
            temp0['scheduled_gap_2']= scheduled_gap_2

            temp0['scheduled_speed_required']= scheduled_speed_required
            temp0['scheduled_speed_required_1']= scheduled_speed_required_1
            temp0['scheduled_speed_required_2']= scheduled_speed_required_2

            temp0['scheduled_speed_increase']= scheduled_speed_increase
            temp0['scheduled_speed_increase_1']= scheduled_speed_increase_1
            temp0['scheduled_speed_increase_2']= scheduled_speed_increase_2

            temp0['attended']=int(attended['attended'])
            temp0['attended_period_1']=attended_period_1
            temp0['attended_period_2']=attended_period_2

            temp0['attended_speed']= attended_speed
            temp0['attended_speed_1']= attended_speed_1
            temp0['attended_speed_2']= attended_speed_2

            temp0['attended_gap']= attended_gap
            temp0['attended_gap_1']= attended_gap_1
            temp0['attended_gap_2']= attended_gap_2

            temp0['attended_speed_required']= attended_speed_required
            temp0['attended_speed_required_1']= attended_speed_required_1
            temp0['attended_speed_required_2']= attended_speed_required_2

            temp0['attended_speed_increase']= attended_speed_increase
            temp0['attended_speed_increase_1']= attended_speed_increase_1
            temp0['attended_speed_increase_2']= attended_speed_increase_2

            temp0['closed']=int(closed['closed'])
            temp0['closed_speed']= closed_speed
            temp0['closed_speed_1']= closed_speed_1
            temp0['closed_speed_2']= closed_speed_2

            temp0['closed_period_1']= closed_period_1
            temp0['closed_period_2']= closed_period_2

            sales_sum.append(temp0)
            print(sales_sum)

        except:
            print('Error')
        print(sales_trainer)
        print(sales_sum)
        return render(request, 'templates/current_kpi.html', {'sales_dates': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'sales_sum': sales_sum
                                                        })

    else:
        return render(request, 'base.html', {})

#ashkahskas

def sales_current_kpi_chart(request):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_trainer=[]
        sales_sum=[]
        sales_dates=[]
        sales_period=[]

        repoting_date = datetime.datetime.now()
        sales_filtered=Record.objects.filter(date__month=repoting_date.month,date__year=repoting_date.year)
        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('-date')
        client_filtered=Client.objects.filter(date_sign_up__month=repoting_date.month,date_sign_up__year=repoting_date.year)
        client_dates=client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        max_days=calendar.monthrange(repoting_date.year,repoting_date.month)[1]
        completed_days=repoting_date.day
        operating_days=max_days-completed_days

        completed_days_1=min(15,completed_days)
        completed_days_2=completed_days-completed_days_1

        operating_days_2=min(max_days-completed_days,max_days-15)
        operating_days_1=operating_days-operating_days_2

        gross_period_1 =float()
        gross_period_2 =float()
        cash_period_1 =float()
        cash_period_2 =float()
        net_eft_period_1 =float()
        net_eft_period_2 =float()
        programs_period_1 =int()
        programs_period_2 =int()

        try:
            for i in range(len(sold_dates)):
                gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
                cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
                eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
                eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))

                if sold_dates[i].day<=15:
                    gross_period_1 = gross_period_1+gross_sale['sales']
                    cash_period_1=cash_period_1+cash['cash']
                    net_eft_period_1=net_eft_period_1+eft_added['eft_added']-eft_loss['eft_loss']
                else:
                    gross_period_2=gross_period_2+gross_sale['sales']
                    cash_period_2=cash_period_2+cash['cash']
                    net_eft_period_2=net_eft_period_2+eft_added['eft_added']-eft_loss['eft_loss']

            for i in range(len(client_dates)):
                programs = client_filtered.filter(date_sign_up=client_dates[i]).aggregate(programs=Count('program_sold_id'))
                if client_dates[i].day<=15:
                    programs_period_1 = programs_period_1+programs['programs']
                else:
                    programs_period_2 = programs_period_2+programs['programs']

            gross_sale = sales_filtered.aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.aggregate(eft_loss=Sum('eft_loss'))
            net_eft=eft_added['eft_added']-eft_loss['eft_loss']
            programs = client_filtered.aggregate(programs=Count('program_sold_id'))

            gross_speed= int(gross_sale['sales']/completed_days)
            cash_speed= round(cash['cash']/completed_days,0)
            net_eft_speed= round(net_eft/completed_days,0)
            programs_speed= round(programs['programs']/completed_days,1)

            if completed_days_1 !=0:
                gross_speed_1 = round(gross_period_1/completed_days_1,0)
                cash_speed_1 = round(cash_period_1/completed_days_1,0)
                net_eft_speed_1 = round(net_eft_period_1/completed_days_1,0)
                programs_speed_1 = round(programs_period_1/completed_days_1,0)

            else:
                gross_speed_1="Period Not Started"
                cash_speed_1="Period Not Started"
                net_eft_speed_1 = "Period Not Started"
                programs_speed_1 = "Period Not Started"

            if completed_days_2 !=0:
                gross_speed_2=int(gross_period_2/completed_days_2)
                cash_speed_2 = round(cash_period_2/completed_days_2,0)
                net_eft_speed_2 = round(net_eft_period_2/completed_days_2,0)
                programs_speed_2 = round(programs_period_2/completed_days_1,0)

            else:
                gross_speed_2='Period Not Started'
                cash_speed_2 = 'Period Not Started'
                net_eft_speed_2 = 'Period Not Started'
                programs_speed_2 = "Period Not Started"

            gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
            cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
            net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))
            programs_target=Target_type.objects.filter(id=5).aggregate(programs_target=Sum('monthly_goal'))

            gross_target_1 = Target_type.objects.filter(id=6).aggregate(gross_target_1=Sum('note1'))
            gross_target_2 = Target_type.objects.filter(id=6).aggregate(gross_target_2=Sum('note2'))
            cash_target_1 = Target_type.objects.filter(id=7).aggregate(cash_target_1=Sum('note1'))
            cash_target_2 = Target_type.objects.filter(id=7).aggregate(cash_target_2=Sum('note2'))
            net_eft_target_1 = Target_type.objects.filter(id=8).aggregate(net_eft_target_1=Sum('note1'))
            net_eft_target_2 = Target_type.objects.filter(id=8).aggregate(net_eft_target_2=Sum('note2'))
            programs_target_1 = Target_type.objects.filter(id=5).aggregate(programs_target_1=Sum('note1'))
            programs_target_2 = Target_type.objects.filter(id=5).aggregate(programs_target_2=Sum('note2'))


            gross_gap=gross_target['gross_target']-gross_sale['sales']
            cash_gap=cash_target['cash_target']-cash['cash']
            net_eft_gap=net_eft_target['net_eft_target']-net_eft
            programs_gap=programs_target['programs_target']-programs['programs']

            gross_gap_1=gross_target_1['gross_target_1']-gross_period_1
            gross_gap_2=gross_target_2['gross_target_2']-gross_period_2
            cash_gap_1=cash_target_1['cash_target_1']-cash_period_1
            cash_gap_2=cash_target_2['cash_target_2']-cash_period_2
            net_eft_gap_1=net_eft_target_1['net_eft_target_1']-net_eft_period_1
            net_eft_gap_2=net_eft_target_2['net_eft_target_2']-net_eft_period_2
            programs_gap_1=programs_target_1['programs_target_1']-programs_period_1
            programs_gap_2=programs_target_2['programs_target_2']-programs_period_2

            if operating_days > 0:
                gross_speed_required= round(gross_gap/operating_days,1)
                if gross_speed >0:
                    gross_speed_increase = round(100*(gross_speed_required/gross_speed-1),2)
                else:
                    gross_speed_increase = "N/A"
                cash_speed_required= round(cash_gap/operating_days,1)
                if cash_speed > 0:
                    cash_speed_increase = round(100*(cash_speed_required/cash_speed-1),2)
                else:
                    cash_speed_increase = "N/A"
                net_eft_speed_required= round(net_eft_gap/operating_days,1)
                if net_eft_speed >0:
                    net_eft_speed_increase = round(100*(net_eft_speed_required/net_eft_speed-1),2)
                else:
                    net_eft_speed_increase = 'N/A'
                programs_speed_required= round(programs_gap/operating_days,1)
                if programs_speed >0:
                    programs_speed_increase = round(100*(programs_speed_required/programs_speed-1),2)
                else:
                    programs_speed_increase = 'N/A'

            else:
                gross_speed_required="No operating days"
                gross_speed_increase = "No Operating days"
                cash_speed_required="No operating days"
                cash_speed_increase = "No Operating days"
                net_eft_speed_required="No operating days"
                net_eft_speed_increase = "No Operating days"
                programs_speed_required="No operating days"
                programs_speed_increase = "No Operating days"

            if operating_days_1 > 0:
                gross_speed_required_1= round(gross_gap_1/operating_days_1,1)
                if type(gross_speed_1)==str or gross_speed_1==0:
                    gross_speed_increase_1 = 0
                else:
                    gross_speed_increase_1 = round(100*(gross_speed_required_1/gross_speed_1-1),2)

                cash_speed_required_1= round(cash_gap_1/operating_days_1,1)
                if type(cash_speed_1)==str or cash_speed_1==0:
                    cash_speed_increase_1=0
                else:
                    cash_speed_increase_1 = round(100*(cash_speed_required_1/cash_speed_1-1),2)

                net_eft_speed_required_1= round(net_eft_gap_1/operating_days_1,1)
                if type(net_eft_speed_1)== str or net_eft_speed_1 ==0:
                    net_eft_speed_increase_1=0
                else:
                    net_eft_speed_increase_1 = round(100*(net_eft_speed_required_1/net_eft_speed_1-1),2)

                programs_speed_required_1= round(programs_gap_1/operating_days_1,1)
                if type(programs_speed_1)==str or programs_speed_1==0:
                    programs_speed_increase_1=0
                else:
                    programs_speed_increase_1 = round(100*(programs_speed_required_1/programs_speed_1-1),2)


            else:
                gross_speed_required_1 = 0
                gross_speed_increase_1 = 0
                cash_speed_required_1 = 0
                cash_speed_increase_1 = 0
                net_eft_speed_required_1 = 0
                net_eft_speed_increase_1 = 0
                programs_speed_required_1 = 0
                programs_speed_increase_1 = 0

            if operating_days_2 > 0:
                gross_speed_required_2= round(gross_gap_2/operating_days_2,1)
                if type(gross_speed_2)==str or gross_speed_2==0:
                    gross_speed_increase_2 = 0
                else:
                    gross_speed_increase_2 = round(100*(gross_speed_required_2/gross_speed_2-1),2)

                cash_speed_required_2= round(cash_gap_2/operating_days_2,1)
                if type(cash_speed_2)==str or cash_speed_2==0:
                    cash_speed_increase_2=0
                else:
                    cash_speed_increase_2 = round(100*(cash_speed_required_2/cash_speed_2-1),2)

                net_eft_speed_required_2= round(net_eft_gap_2/operating_days_2,1)
                if type(net_eft_speed_2)== str or net_eft_speed_2 ==0:
                    net_eft_speed_increase_2=0
                else:
                    net_eft_speed_increase_2 = round(100*(net_eft_speed_required_2/net_eft_speed_2-1),2)
                programs_speed_required_2= round(programs_gap_2/operating_days_2,1)
                if type(programs_speed_2)==str or programs_speed_2==0:
                    programs_speed_increase_2=0
                else:
                    programs_speed_increase_2 = round(100*(programs_speed_required_2/programs_speed_2-1),2)


            else:
                gross_speed_required_2 = 0
                gross_speed_increase_2 = 0
                cash_speed_required_2 = 0
                cash_speed_increase_2 = 0
                net_eft_speed_required_2 = 0
                net_eft_speed_increase_2 = 0
                programs_speed_required_2 = 0
                programs_speed_increase_2 = 0

            temp0=dict()
            temp0['gross_sale']=int(gross_sale['sales'])
            temp0['gross_period_1']=int(gross_period_1)
            temp0['gross_period_2']=int(gross_period_2)

            temp0['gross_speed']=int(gross_speed)
            temp0['gross_speed_1']=int(gross_speed_1)
            temp0['gross_speed_2']=int(gross_speed_2)

            temp0['gross_gap']=int(gross_gap)
            temp0['gross_gap_1']=int(gross_gap_1)
            temp0['gross_gap_2']=int(gross_gap_2)

            temp0['gross_speed_required']=gross_speed_required
            temp0['gross_speed_required_1']=gross_speed_required_1
            temp0['gross_speed_required_2']=gross_speed_required_2

            temp0['gross_speed_increase']=gross_speed_increase
            temp0['gross_speed_increase_1']=gross_speed_increase_1
            temp0['gross_speed_increase_2']=gross_speed_increase_2

            temp0['cash']=int(cash['cash'])
            temp0['cash_period_1']=int(cash_period_1)
            temp0['cash_period_2']=int(cash_period_2)
            temp0['cash_speed']=cash_speed
            temp0['cash_speed_1']=cash_speed_1
            temp0['cash_speed_2']=cash_speed_2

            temp0['cash_gap']=cash_gap
            temp0['cash_gap_1']=cash_gap_1
            temp0['cash_gap_2']=cash_gap_2

            temp0['cash_speed_required']=cash_speed_required
            temp0['cash_speed_required_1']=cash_speed_required_1
            temp0['cash_speed_required_2']=cash_speed_required_2

            temp0['cash_speed_increase']=cash_speed_increase
            temp0['cash_speed_increase_1']=cash_speed_increase_1
            temp0['cash_speed_increase_2']=cash_speed_increase_2

            temp0['net_eft']=int(net_eft)
            temp0['net_eft_period_1']=int(net_eft_period_1)
            temp0['net_eft_period_2']=int(net_eft_period_2)

            temp0['net_eft_speed']=int(net_eft_speed)
            temp0['net_eft_speed_1']=int(net_eft_speed_1)
            temp0['net_eft_speed_2']=int(net_eft_speed_2)

            temp0['net_eft_gap']=net_eft_gap
            temp0['net_eft_gap_1']=net_eft_gap_1
            temp0['net_eft_gap_2']=net_eft_gap_2

            temp0['net_eft_speed_required']=net_eft_speed_required
            temp0['net_eft_speed_required_1']=net_eft_speed_required_1
            temp0['net_eft_speed_required_2']=net_eft_speed_required_2

            temp0['net_eft_speed_increase']=net_eft_speed_increase
            temp0['net_eft_speed_increase_1']=net_eft_speed_increase_1
            temp0['net_eft_speed_increase_2']=net_eft_speed_increase_2

            temp0['programs']=int(programs['programs'])
            temp0['programs_period_1']=programs_period_1
            temp0['programs_period_2']=programs_period_2

            temp0['programs_speed']= programs_speed
            temp0['programs_speed_1']= programs_speed_1
            temp0['programs_speeds_2']= programs_speed_2

            temp0['programs_gap']= programs_gap
            temp0['programs_gap_1']=programs_gap_1
            temp0['programs_gap_2']=programs_gap_2

            temp0['programs_speed_required']= programs_speed_required
            temp0['programs_speed_required_1']= programs_speed_required_1
            temp0['programs_speed_required_2']= programs_speed_required_2

            temp0['programs_speed_increase']= programs_speed_increase
            temp0['programs_speed_increase_1']= programs_speed_increase_1
            temp0['programs_speed_increase_2']= programs_speed_increase_2

            sales_sum.append(temp0)
            print(sales_sum)

        except:
            print('Error')

        return render(request, 'templates/current_kpi_chart.html', {'sales_dates': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                              'sales_sum': sales_sum})

    else:
        return render(request, 'base.html', {})
