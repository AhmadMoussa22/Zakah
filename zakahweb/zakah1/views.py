#!/usr/bin/python
#  -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .MyClasses import auxilary
from .formshtml import signin_form, monthlysave_form
from .models import zakah_register_c, zakah_summary_c
import datetime, operator, time
from datetime import date,timedelta
from django.urls import reverse
# Create your views here.
# cd c:\work\python work\zakah\zakah\zakahweb
# python manage.py runserver
# request.session['mes_main'] = ''
# mess_main = request.session.get('mes_main')

my_aux=auxilary()
seq_deduct=my_aux.deduct_till_zero
update_values_dates=my_aux.update_objects



def main_f(request):
    mess_main=request.session.get('mes_main')
    request.session['mes_main']=''
    form_f=signin_form
    if request.user.is_authenticated():  # check user logged in
        user_name = request.user.username
        return render(request, 'main_t.html', {'name': user_name,'mess':mess_main})
    return render (request,'main_t.html',{'mess':mess_main,'f':form_f})

################################################################

################################################################
def signup_f(request):
    if not request.user.is_authenticated():
        if request.method=='POST':
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['password']
            firstname=request.POST['fname']
            lastname=request.POST['lname']
            try:  # to check for username duplication error
                newuser =User.objects.create_user(username, email, password)
                newuser.first_name=firstname
                newuser.last_name=lastname
                newuser.save()
                updatesummary_o = zakah_summary_c()
                updatesummary_o.username = User.objects.get(username=user_name)
                updatesummary_o.total_saving = 0
                updatesummary_o.nesab_day = date(1111, 1, 1)
                updatesummary_o.required_zakah = 0
                updatesummary_o.save()
                login(request,newuser)
                return HttpResponseRedirect(reverse('main'))
            except:
                request.session['mes_main'] = 'اسم المستخدم موجود بالفعل برجاء اختيار اسم اخر'
    request.session['mes_main'] = 'انت بالمفعل مسجل دخولك'
    return HttpResponseRedirect(reverse('main'))

#####################################################################

#####################################################################

def signin_f(request):
    #m = request.session.get('mes') #receive data written by another view function
    #request.session['mes']='' #initialize the message container
    if not request.user.is_authenticated():
        if request.method == 'POST':
            form_f=signin_form(request.POST)
            if form_f.is_valid():
                user_name = form_f.cleaned_data['user_name']
                pass_word = form_f.cleaned_data['pass_word']
                print user_name, pass_word,
                res = authenticate(username=user_name, password=pass_word)
                if res is not None:
                    login(request, res)
                    return HttpResponseRedirect('/zakah1/main/')
                else:
                    request.session['mes_main']='اسم المستخدم او كلمة المرور غير صحيحة'
                    return HttpResponseRedirect(reverse('main'))
    else:
        form_f = signin_form()
    return HttpResponseRedirect(reverse('main'))

#######################################################################

#######################################################################

def update_DB_f(request):
    if request.user.is_authenticated():#check user loged in else redirect to signin with message
        user_name = request.user.username
        if request.method == 'POST':
            updatedetails_o = zakah_register_c()
            updatesummary_o = zakah_summary_c.objects.get(username=User.objects.get(username=user_name))
            nesab = 80000
            if updatesummary_o.total_saving < nesab:
                nesab_acheived = False
            else:
                nesab_acheived = True
            monthly_form = monthlysave_form(request.POST)
            if monthly_form.is_valid():
                saving_date = monthly_form.cleaned_data['month_save_date']
                saving_amount = monthly_form.cleaned_data['month_save_le']
                year, month = saving_date.split('-')
                parsed_saving_date = datetime.date(int(year), int(month), 1)

                ###############################################################################
                ### assign fixed values to object(username,saving,saving date -- default values assigned through class inModels.py
                updatedetails_o.username = User.objects.get(username=user_name)
                updatedetails_o.saving_day = parsed_saving_date
                updatedetails_o.saving = float(saving_amount)
                # assign other parameters to object(active,active saving,zakah)--> then save to DB
                net_save_icrease = saving_amount - updatesummary_o.total_saving
                if net_save_icrease <= 0:
                    updatedetails_o.active_saving = 0
                    updatedetails_o.active = False
                else:
                    updatedetails_o.active_saving = net_save_icrease

                updatedetails_o.zakah = 0.025 * int(updatedetails_o.active_saving)
                updatedetails_o.save()
                ##Now then all parameters of object of zakah register assigned initial values and saved


                ################################################################################################
                # Values that need algorithms: Active zakah(any change of it requires change in zakah),Start date,Deserve date,and Active
                ################################################################################################

                ###############################################################################################
                # if withdrawl deduct it from previous active saving one by one starting by latest saving date(consequently modify zakah)
                # in same time if any active saving became 0 after deduction; modify 'active' to False, start and deserve dates to initial
                list_zakahdetails = zakah_register_c.objects.filter(username=User.objects.get(username=user_name),
                                                                    active=True)
                if net_save_icrease < 0:
                    seq_deduct(net_save_icrease, list_zakahdetails)  # a function to execute the above description

                    # assign start and deserve dates based on previous and current 'nesab acheived' status
                    # first update total saving in 'zakah summary' table
                updatesummary_o.total_saving = updatedetails_o.saving
                updatesummary_o.save()

                # case1: previous nesab not achieved and new not acheived-->No change; keep start and deserve dates with initial values
                # case2: previous nesab not achieved and new acheived--> update start date of all active saving to be the saving date,
                # consequently update deserve date to be 354 days later...update nesab date in zakah summary table
                # case3: previous nesab achieved and new acheived(with entry deposite not ithdrawl)-->update start date of the current
                # row to be saving date;consequently update deserve date to be 354 days later
                # case4: previous nesab not achieved and new not acheived-->update start date and deserve date of all active rows to
                # initial value...update nesab date in zakah summary table
                if updatesummary_o.total_saving < nesab:
                    updated_nesab_acheived = False
                else:
                    updated_nesab_acheived = True

                updatesummary_o, updatedetails_o, list_zakahdetails = update_values_dates(nesab_acheived,
                                                                                          updated_nesab_acheived,
                                                                                          updatesummary_o,
                                                                                          updatedetails_o,
                                                                                          list_zakahdetails)
            else:
                monthly_form = monthlysave_form()
                request.session['mes'] = 'برجاء ادخال جميع البيانات بصورة صحيحة'
        return HttpResponseRedirect(reverse('main'))
    request.session['mes_main'] ='برجاء تسجيل الدخول اولا ثم تحديث بيانات مدخراتك'#sending message to main_f function
    return HttpResponseRedirect(reverse('main'))

########################################################################

########################################################################

def signout_f(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))
