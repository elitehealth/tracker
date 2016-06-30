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
    current_user = request.user.id
    restricted_group = models.Group.objects.get(id=2)
    restricted_users = restricted_group.user_set.filter(id=current_user)

    if request.user.is_authenticated() and len(restricted_users)>0:
        return redirect("add_client")

    elif request.user.is_authenticated() and len(restricted_users)==0:
        return render(request, 'templates/index.html',{})

    else:
        return render(request, 'base.html',{})

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


