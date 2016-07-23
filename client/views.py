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
from appointment.models import appointment
import calendar

def home(request):
    return render(request, 'base.html',{})


def client_info(request):

    if request.user.is_authenticated():

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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

        for i in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'))
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

            if sold_dates[i].day<=15:
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
        program = client_filtered.aggregate(program=Count('program_sold'))
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
        if program['program'] is None:
            program['programm']=0
        else:
            print('')
        net_eft=eft_added['eft_added']-eft_loss['eft_loss']
        gross_speed= int(gross_sale['sales']/completed_days)
        cash_speed= round(cash['cash']/completed_days,0)
        net_eft_speed= round(net_eft/completed_days,0)

        if completed_days_1 !=0:
            gross_speed_1 = round(gross_period_1/completed_days_1,0)
            cash_speed_1 = round(cash_period_1/completed_days_1,0)
            net_eft_speed_1 = round(net_eft_period_1/completed_days_1,0)
        else:
            gross_speed_1=0
            cash_speed_1=0
            net_eft_speed_1 = 0

        if completed_days_2 !=0:
            gross_speed_2=int(gross_period_2/completed_days_2)
            cash_speed_2 = round(cash_period_2/completed_days_2,0)
            net_eft_speed_2 = round(net_eft_period_2/completed_days_2,0)

        else:
            gross_speed_2=0
            cash_speed_2 = 0
            net_eft_speed_2 = 0

        gross_target=Target_type.objects.filter(id=6).aggregate(gross_target=Sum('monthly_goal'))
        cash_target=Target_type.objects.filter(id=7).aggregate(cash_target=Sum('monthly_goal'))
        net_eft_target=Target_type.objects.filter(id=8).aggregate(net_eft_target=Sum('monthly_goal'))


        gross_target_1 = Target_type.objects.filter(id=6).aggregate(gross_target_1=Sum('note1'))
        gross_target_2 = Target_type.objects.filter(id=6).aggregate(gross_target_2=Sum('note2'))
        cash_target_1 = Target_type.objects.filter(id=7).aggregate(cash_target_1=Sum('note1'))
        cash_target_2 = Target_type.objects.filter(id=7).aggregate(cash_target_2=Sum('note2'))
        net_eft_target_1 = Target_type.objects.filter(id=8).aggregate(net_eft_target_1=Sum('note1'))
        net_eft_target_2 = Target_type.objects.filter(id=8).aggregate(net_eft_target_2=Sum('note2'))


        gross_gap=-(gross_target['gross_target']-gross_sale['sales'])
        cash_gap=-(cash_target['cash_target']-cash['cash'])
        net_eft_gap=-(net_eft_target['net_eft_target']-net_eft)

        gross_gap_1=gross_target_1['gross_target_1']-gross_period_1
        gross_gap_2=gross_target_2['gross_target_2']-gross_period_2
        cash_gap_1=cash_target_1['cash_target_1']-cash_period_1
        cash_gap_2=cash_target_2['cash_target_2']-cash_period_2
        net_eft_gap_1=net_eft_target_1['net_eft_target_1']-net_eft_period_1
        net_eft_gap_2=net_eft_target_2['net_eft_target_2']-net_eft_period_2

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

        else:
            gross_speed_required="No operating days"
            gross_speed_increase = "No Operating days"
            cash_speed_required="No operating days"
            cash_speed_increase = "No Operating days"
            net_eft_speed_required="No operating days"
            net_eft_speed_increase = "No Operating days"

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

        else:
            gross_speed_required_1 = "Completed Period"
            gross_speed_increase_1 = "Completed Period"
            cash_speed_required_1 = "Completed Period"
            cash_speed_increase_1 = "Completed Period"
            net_eft_speed_required_1 = "Completed Period"
            net_eft_speed_increase_1 = "Completed Period"

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

        else:
            gross_speed_required_2 = "Completed Period"
            gross_speed_increase_2 = "Completed Period"
            cash_speed_required_2 = "Completed Period"
            cash_speed_increase_2 = "Completed Period"
            net_eft_speed_required_2 = "Completed Period"
            net_eft_speed_increase_2 = "Completed Period"



        program_speed= round(program['program']/completed_days,1)
        program_target=Target_type.objects.filter(id=5).aggregate(program_target=Sum('monthly_goal'))
        program_gap=-(program_target['program_target']-program['program'])
        program_speed_required= round(program_gap/operating_days,0)
        if program_speed != 0:
            program_speed_increase = round(100*(program_speed_required/program_speed-1),2)
        else:
            program_speed_increase = 0

        for i in range(len(appointment_dates)):
            requests = appointment_filtered.filter(date=appointment_dates[i]).aggregate(request=Sum('consultations_requested'))
            scheduled = appointment_filtered.filter(date=appointment_dates[i]).aggregate(scheduled=Sum('consultations_scheduled'))
            closed = appointment_filtered.filter(date=appointment_dates[i]).aggregate(closed=Sum('consultations_closed'))
            attended = appointment_filtered.filter(date=appointment_dates[i]).aggregate(attended=Sum('consultations_closed'))
            if requests['request'] is None:
                requests['request']=0
            else:
                print('')
            if scheduled['scheduled'] is None:
                scheduled['scheduled']=0
            else:
                print('')
            if closed['closed'] is None:
                closed['closed']=0
            else:
                print('')
            if attended['attended'] is None:
                attended['attended']=0
            else:
                print('')


            if appointment_dates[i].day<=15:
                requests_period_1 = requests_period_1+requests['request']
                scheduled_period_1= scheduled_period_1 + scheduled['scheduled']
                closed_period_1 = closed_period_1 + closed['closed']
                attended_period_1 = attended_period_1 + attended['attended']
            else:
                requests_period_2 = requests_period_2+requests['request']
                scheduled_period_2= scheduled_period_2 + scheduled['scheduled']
                closed_period_2 = closed_period_2 + closed['closed']
                attended_period_2 = attended_period_2 + attended['attended']

        consultation_request = appointment_filtered.aggregate(request=Sum('consultations_requested'))
        if consultation_request['request'] is None:
            consultation_request['request']=0
        else:
            print('')
        request_target=Target_type.objects.filter(id=2).aggregate(request_target=Sum('monthly_goal'))
        request_speed= round(consultation_request['request']/completed_days,1)
        request_gap=-(request_target['request_target']-consultation_request['request'])
        request_speed_required= round(request_gap/operating_days,0)
        if request_speed != 0:
            request_speed_increase = round(100*(request_speed_required/request_speed-1),2)
        else:
           request_speed_increase = 0

        consultation_scheduled = appointment_filtered.aggregate(scheduled=Sum('consultations_scheduled'))
        if consultation_scheduled['scheduled'] is None:
            consultation_scheduled['scheduled']=0
        else:
            print('')

        scheduled_target=Target_type.objects.filter(id=3).aggregate(scheduled=Sum('monthly_goal'))
        scheduled_speed= round(consultation_scheduled['scheduled']/completed_days,1)
        scheduled_gap=-(scheduled_target['scheduled']-consultation_scheduled['scheduled'])
        scheduled_speed_required= round(scheduled_gap/operating_days,0)
        if scheduled_speed != 0:
            scheduled_speed_increase = round(100*(scheduled_speed_required/scheduled_speed-1),2)
        else:
            scheduled_speed_increase = 0

        consultation_attended = appointment_filtered.aggregate(attended=Sum('consultations_attended'))
        if consultation_attended['attended'] is None:
            consultation_attended['attended']=0
        else:
            print('')
        attended_target=Target_type.objects.filter(id=4).aggregate(attended=Sum('monthly_goal'))
        attended_speed= round(consultation_attended['attended']/completed_days,1)
        attended_gap=-(attended_target['attended']-consultation_attended['attended'])
        attended_speed_required= round(attended_gap/operating_days,0)
        if attended_speed != 0:
            attended_speed_increase = round(100*(attended_speed_required/attended_speed-1),2)
        else:
            attended_speed_increase = 0

        consultation_closed = appointment_filtered.aggregate(closed=Sum('consultations_closed'))
        if consultation_closed['closed'] is None:
            consultation_closed['closed']=0
        else:
            print('')
        closed_speed= round(consultation_closed['closed']/completed_days,1)

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

        temp0['program']=int(program['program'])
        temp0['program_speed']=program_speed
        temp0['program_gap']=program_gap
        temp0['program_speed_required']=program_speed_required
        temp0['program_speed_increase']=program_speed_increase

        temp0['request']=int(consultation_request['request'])
        temp0['request_speed']=request_speed
        temp0['request_period_1']=requests_period_1
        temp0['request_period_2']=requests_period_2
        temp0['request_gap']=request_gap
        temp0['request_speed_required']= request_speed_required
        temp0['request_speed_increase']= request_speed_increase

        temp0['scheduled']=int(consultation_scheduled['scheduled'])
        temp0['scheduled_period_1']=scheduled_period_1
        temp0['scheduled_period_2']=scheduled_period_2
        temp0['scheduled_speed']= scheduled_speed
        temp0['scheduled_gap']= scheduled_gap
        temp0['scheduled_speed_required']= scheduled_speed_required
        temp0['scheduled_speed_increase']= scheduled_speed_increase

        temp0['attended']=int(consultation_attended['attended'])
        temp0['attended_period_1']=attended_period_1
        temp0['attended_period_2']=attended_period_2
        temp0['attended_speed']= attended_speed
        temp0['attended_gap']= attended_gap
        temp0['attended_speed_required']= attended_speed_required
        temp0['attended_speed_increase']= attended_speed_increase

        temp0['closed']=int(consultation_closed['closed'])
        temp0['closed_speed']= closed_speed
        temp0['closed_period_1']= closed_period_1
        temp0['closed_period_2']= closed_period_2

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

        print(sales_sum)
        print(sales_trainer)

        print(sales_sum)
        return render(request, 'templates/index.html', {'sales_dates': sales_dates,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
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
        sales_client_1=[]
        sales_client_2=[]

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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

        Client_filtered=Client.objects.filter(date_sign_up__month=slicer2,date_sign_up__year=slicer1)
        client_list=Client_filtered.values_list('client_name', flat=True).distinct().order_by('client_name')

        client_filtered_1=Client_filtered.filter(date_sign_up__lte=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0))
        client_list_1=client_filtered_1.values_list('client_name', flat=True).distinct().order_by('client_name')

        client_filtered_2=Client_filtered.filter(date_sign_up__gt=datetime.datetime(year_rep, month_rep, 15, 0, 0, 0))
        client_list_2=client_filtered_2.values_list('client_name', flat=True).distinct().order_by('client_name')

        client_date=Client_filtered.values_list('date_sign_up', flat=True).distinct().order_by('-date_sign_up')

        for i in range(len(client_list)):
            client_name = client_list[i]
            gross_sale = Client_filtered.filter(client_name=client_list[i]).aggregate(sales=Sum('gross_sale'))
            cash = Client_filtered.filter(client_name=client_list[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = Client_filtered.filter(client_name=client_list[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = Client_filtered.filter(client_name=client_list[i]).aggregate(eft_loss=Sum('eft_loss'))
            lead_source_list = Client_filtered.filter(client_name=client_list[i]).values_list('lead_source_id',flat=True).distinct()
            lead_source = str()
            for k in range(len(lead_source_list)):
                lead_source = lead_source +Lead.objects.filter(id=lead_source_list[k]).values_list('name')[0][0] + ", "
            program_list = Client_filtered.filter(client_name=client_list[i]).values_list('program_sold_id',flat=True).distinct()
            programs = str()
            for j in range(len(program_list)):
                programs = programs +Program.objects.filter(id=program_list[j]).values_list('name')[0][0] + ", "

            temp=dict()
            temp['client']=client_name
            temp['date']=client_date
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss
            temp['lead']=lead_source
            temp['program']=programs

            sales_client.append(temp)


        for i in range(len(client_list_1)):
            client_name = client_list_1[i]
            gross_sale = client_filtered_1.filter(client_name=client_list_1[i]).aggregate(sales=Sum('gross_sale'))
            cash = client_filtered_1.filter(client_name=client_list_1[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = client_filtered_1.filter(client_name=client_list_1[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = client_filtered_1.filter(client_name=client_list_1[i]).aggregate(eft_loss=Sum('eft_loss'))
            lead_source_list = client_filtered_1.filter(client_name=client_list_1[i]).values_list('lead_source_id',flat=True).distinct()
            lead_source = str()
            for k in range(len(lead_source_list)):
                lead_source = lead_source +Lead.objects.filter(id=lead_source_list[k]).values_list('name')[0][0] + ", "
            program_list = client_filtered_1.filter(client_name=client_list_1[i]).values_list('program_sold_id',flat=True).distinct()
            programs = str()
            for j in range(len(program_list)):
                programs = programs +Program.objects.filter(id=program_list[j]).values_list('name')[0][0] + ", "

            temp=dict()
            temp['client']=client_name
            temp['date']=client_date
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss
            temp['lead']=lead_source
            temp['program']=programs

            sales_client_1.append(temp)

        for i in range(len(client_list_2)):
            client_name = client_list_2[i]
            gross_sale = client_filtered_2.filter(client_name=client_list_2[i]).aggregate(sales=Sum('gross_sale'))
            cash = client_filtered_2.filter(client_name=client_list_2[i]).aggregate(cash=Sum('cash_recieved'))
            eft_added = client_filtered_2.filter(client_name=client_list_2[i]).aggregate(eft_added=Sum('eft_added'))
            eft_loss = client_filtered_2.filter(client_name=client_list_2[i]).aggregate(eft_loss=Sum('eft_loss'))
            lead_source_list = client_filtered_2.filter(client_name=client_list_2[i]).values_list('lead_source_id',flat=True).distinct()
            lead_source = str()
            for k in range(len(lead_source_list)):
                lead_source = lead_source +Lead.objects.filter(id=lead_source_list[k]).values_list('name')[0][0] + ", "
            program_list = client_filtered_2.filter(client_name=client_list_2[i]).values_list('program_sold_id',flat=True).distinct()
            programs = str()
            for j in range(len(program_list)):
                programs = programs +Program.objects.filter(id=program_list[j]).values_list('name')[0][0] + ", "

            temp=dict()
            temp['client']=client_name
            temp['date']=client_date
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss
            temp['lead']=lead_source
            temp['program']=programs

            sales_client_2.append(temp)

        return render(request, 'templates/table_client.html', {'sales_client_1': sales_client_1,'sales_client_2': sales_client_2, 'sales_client': sales_client,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),'list_of_slicer': list_of_slicer })

    else:
        return render(request, 'base.html', {})

def chart(request,slicer1,slicer2):

    current_user = str(request.user.id)
    if request.user.is_authenticated():
        sales_lead=[]
        sales_trainer=[]
        sales_client=[]
        sales_program=[]
        sales_dates = []

        months = Client.objects.values_list('date_sign_up',flat=True).distinct().order_by('-date_sign_up')
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

        sales_filtered=Record.objects.filter(date__month=slicer2,date__year=slicer1)

        sold_dates=sales_filtered.values_list('date', flat=True).distinct().order_by('date')
        for i in range(len(sold_dates)):
            gross_sale = sales_filtered.filter(date=sold_dates[i]).aggregate(sales=Sum('gross_sale'), max_sales=Max('gross_sale'))
            cash = sales_filtered.filter(date=sold_dates[i]).aggregate(cash=Sum('cash_recieved'), max_cash=Max('cash_recieved'))
            eft_added = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_added=Sum('eft_added'), max_eft_added=Max('eft_added'))
            eft_loss = sales_filtered.filter(date=sold_dates[i]).aggregate(eft_loss=Sum('eft_loss'), max_eft_loss=Max('eft_loss'))

            temp=dict()
            temp['date']=sold_dates[i].strftime("%a, %d")
            temp['gross']=gross_sale
            temp['cash']=cash
            temp['eft_added']=eft_added
            temp['eft_loss']=eft_loss

            sales_dates.append(temp)
        print(sales_dates)
        return render(request, 'templates/client_chart.html', {'sales_lead': sales_lead,'sales_trainer': sales_trainer,
                                                               'sales_client': sales_client,'sales_program': sales_program,
                                                               'reporting_date': repoting_date.strftime("%B, %Y"),
                                                               'list_of_slicer': list_of_slicer, 'sales_dates': sales_dates })

    else:
        return render(request, 'base.html', {})


