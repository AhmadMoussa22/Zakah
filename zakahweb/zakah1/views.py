#!/usr/bin/python
#  -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .MyClasses import auxilary
from .forms import signin_form
from .models import zakah_register_c, zakah_summary_c
import datetime, operator, time
from datetime import date,timedelta

# Create your views here.
# cd c:\work\python work\zakah\zakah\zakahweb
# python manage.py runserver

def main_f(request):
    f=signin_form()
    if request.user.is_authenticated():  # check user loged in else redirect to signin with message


###########################################################################
# declare and assign: 'username' from authenticatin, object for zakah register table, object for zakah summary table,
# 'Nesab' value(constant) , previous nesab acheived status from the last 'total saving' value
        user_name = request.user.username
        updatedetails_o = zakah_register_c()
        updatesummary_o = zakah_summary_c.objects.get(username=User.objects.get(username=user_name))
        nesab = 80000
        if updatesummary_o.total_saving < nesab:
            nesab_acheived = False
        else:
            nesab_acheived = True


############################################################################
# When submit clicked; Read data from HTML form; 'in/out', 'saving amount', 'saving day'
        if request.method == 'POST':
            in_out = request.POST['in_out']  # deposite or withdrawl
            saving_date = request.POST['saving_date']
            year, month, day = saving_date.split('-')
            parsed_saving_date = datetime.date(int(year), int(month), int(day))  # reformat date to match django
            saving_amount = int(request.POST['saving_amount'])

###############################################################################
### assign fixed values to object -- default values assigned through class inModels.py
            # if 'in-out'=out;saving amount to be negative, active saving to be 0,active(default=true) to be false else active saving=savig amount
            if in_out == 'out':
                saving_amount = int(saving_amount) * -1
                updatedetails_o.active_saving = 0
                updatedetails_o.active = False
            else:
                updatedetails_o.active_saving = saving_amount
# assign other parameters to object:username,saving day, zakah--> then save to DB
            updatedetails_o.username = User.objects.get(username=user_name)
            updatedetails_o.saving_day = parsed_saving_date
            updatedetails_o.saving = float(saving_amount)
            updatedetails_o.zakah = 0.025 * int(updatedetails_o.active_saving)
            # updatedetails_o.start_day=date(1111,1,1)
            # updatedetails_o.deserve_day=date(1111,1,1)#parsed_saving_date+timedelta(days=354)
            updatedetails_o.save()
##Now then all parameters of object of zakah register assigned initial values and saved


################################################################################################
# Values that need algorithms: Active zakah(any change of it requires change in zakah),Start date,Deserve date,and Active
################################################################################################

###############################################################################################
#if deposite deduct it from previous active saving one by one starting by latest saving date(consequently modify zakah)
#in same time if any active saving became 0 after deduction; modify 'active' to False, start and deserve dates to initial
            list_zakahdetails = zakah_register_c.objects.filter(active=True)
            if updatedetails_o.saving < 0:
                active_indication = updatedetails_o.saving
                list_zakahdetails = sorted(list_zakahdetails, key=operator.attrgetter('saving_day'),reverse=True)
                #to arrange a queryset
                for i in list_zakahdetails:
                    active_indication = active_indication + i.active_saving
                    if active_indication <= 0:
                        i.active_saving = 0
                        i.zakah = i.active_saving * .025
                        i.active = False
                        i.start_day = date(1111, 1, 1)
                        i.deserve_day = date(1111, 1, 1)
                        i.save()
                    else:
                        i.active_saving = active_indication
                        i.zakah = i.active_saving * .025
                        i.save()
                        break

#assign start and deserve dates based on previous and current 'nesab acheived' status
#first calculate total saving and update 'zakah summary' table
            all_zakah_rows = zakah_register_c.objects.all()
            total_saving = 0
            for i in all_zakah_rows:
                total_saving = total_saving + i.saving
            updatesummary_o.total_saving = total_saving
            updatesummary_o.save()

# case1: previous nesab not achieved and new not acheived-->No change; keep start and deserve dates with initial values
# case2: previous nesab not achieved and new acheived--> update start date of all active saving to be the saving date,
# consequently update deserve date to be 354 days later...update nesab date in zakah summary table
# case3: previous nesab achieved and new acheived(with entry deposite not ithdrawl)-->update start date of the current
# row to be saving date;consequently update deserve date to be 354 days later
# case4: previous nesab not achieved and new not acheived-->update start date and deserve date of all active rows to
# initial value...update nesab date in zakah summary table
            if nesab_acheived == False:
                if updatesummary_o.total_saving >= nesab:  # old nesab False and new nesab True
                    updatesummary_o.nesab_day = updatedetails_o.saving_day
                    updatesummary_o.save()
                    for i in list_zakahdetails:
                        i.start_day = updatedetails_o.saving_day
                        i.deserve_day = updatedetails_o.saving_day + timedelta(days=354)
                        i.save()
            else:  # old nesab check = True
                if updatesummary_o.total_saving > nesab:  # neew nesab True
                    if updatedetails_o.active:  # deposite not withdrawll
                        updatedetails_o.start_day = updatedetails_o.saving_day
                        updatedetails_o.deserve_day = updatedetails_o.saving_day + timedelta(days=354)
                        updatedetails_o.save()
                else:  # old nesab True and new nesab False
                    updatesummary_o.nesab_day = date(1111, 1, 1)
                    updatesummary_o.save()
                    for i in list_zakahdetails:
                        i.start_day = date(1111, 1, 1)
                        i.deserve_day = date(1111, 1, 1)
                        i.save()

            return HttpResponseRedirect('/zakah1/main')
        return render(request, 'profile.html', {'name': user_name})
    request.session['mes'] = 'Please sign in before accessing your profile page'  # writing data in public container
#  to be used by othe view functions
    return HttpResponseRedirect('/zakah1/signin')
    #return render (request,'main_t.html',{'f':f})

################################################################

################################################################
def signup_f(request):
    f1=signin_form(request.POST or None)
    mess=''
    my_auxilary = auxilary()
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
            return HttpResponseRedirect('/zakah1/main/')
        except:
            mess='Duplicated Data'
    return render(request, 'sign up.html', {'d':mess,'f':f1})

#####################################################################

#####################################################################

def signin_f(request):
    m = request.session.get('mes') #receive data written by another view function
    request.session['mes']='' #initialize the message container
    print m #use the received message
    if request.user.is_authenticated():
        return HttpResponseRedirect('/zakah1/profile')
    if request.method == 'POST':
        user_name = request.POST['user_name']
        pass_word = request.POST['pass_word']
        res = authenticate(username=user_name, password=pass_word)
        if res is not None:
            login(request, res)
            return HttpResponseRedirect('/zakah1/main/')
        else:
            mess='Eigther username or password is incorrect'
            return render(request,'sign in.html',{'mess':mess})
    return render(request,'sign in.html',{})

#######################################################################

#######################################################################

def profile_f(request):
    if request.user.is_authenticated():#check user loged in else redirect to signin with message


###########################################################################
#declare and assign: 'username' from authenticatin, object for zakah register table, object for zakah summary table,
#'Nesab' value(constant) , previous nesab acheived status from the last 'total saving' value
        user_name=request.user.username
        updatedetails_o = zakah_register_c()
        updatesummary_o = zakah_summary_c.objects.get(username=User.objects.get(username=user_name))
        nesab=80000
        if updatesummary_o.total_saving < nesab :
            nesab_acheived=False
        else:
            nesab_acheived=True


############################################################################
#When submit clicked; Read data from HTML form; 'in/out', 'saving amount', 'saving day'
        if request.method == 'POST':
            in_out = request.POST['in_out']#deposite or withdrawl
            saving_date = request.POST['saving_date']
            year, month, day = saving_date.split('-')
            parsed_saving_date = datetime.date(int(year),int(month),int(day))#reformat date to match django
            saving_amount=int(request.POST['saving_amount'])


###############################################################################
### assign fixed values to object -- default values assigned through class inModels.py
#if 'in-out'=out;saving amount to be negative, active saving to be 0,active(default=true) to be false else active saving=savig amount
            if in_out == 'out':
                saving_amount=int(saving_amount)*-1
                updatedetails_o.active_saving=0
                updatedetails_o.active=False
            else:
                updatedetails_o.active_saving=saving_amount
#assign other parameters to object:username,saving day, zakah--> then save to DB
            updatedetails_o.username=User.objects.get(username=user_name)
            updatedetails_o.saving_day=parsed_saving_date
            updatedetails_o.saving=float(saving_amount)
            updatedetails_o.zakah=0.025*int(updatedetails_o.active_saving)
            #updatedetails_o.start_day=date(1111,1,1)
            #updatedetails_o.deserve_day=date(1111,1,1)#parsed_saving_date+timedelta(days=354)
            updatedetails_o.save()
##Now then all parameters of object of zakah register assigned initial values and saved


################################################################################################
#Values that need algorithms: Active zakah(any change of it requires change in zakah),Start date,Deserve date,and Active
################################################################################################

###############################################################################################
# if deposite deduct it from previous active saving one by one starting by latest saving date(consequently modify zakah)
# in same time if any active saving became 0 after deduction; modify 'active' to False, start and deserve dates to initial
            list_zakahdetails=zakah_register_c.objects.filter(active=True)
            if updatedetails_o.saving<0:
                active_indication = updatedetails_o.saving
                list_zakahdetails = sorted(list_zakahdetails, key=operator.attrgetter('saving_day'),reverse=True)#to arrange a queryset
                for i in list_zakahdetails:
                    active_indication = active_indication + i.active_saving
                    if active_indication<=0:
                        i.active_saving =0
                        i.zakah=i.active_saving*.025
                        i.active=False
                        i.start_day=date(1111,1,1)
                        i.deserve_day=date(1111,1,1)
                        i.save()
                    else:
                        i.active_saving = active_indication
                        i.zakah=i.active_saving*.025
                        i.save()
                        break

#assign start and deserve dates based on previous and current 'nesab acheived' status
#first calculate total saving and update 'zakah summary' table
            all_zakah_rows=zakah_register_c.objects.all()
            total_saving=0
            for i in all_zakah_rows:
                total_saving=total_saving+i.saving
            updatesummary_o.total_saving=total_saving
            updatesummary_o.save()

#case1: previous nesab not achieved and new not acheived-->No change; keep start and deserve dates with initial values
#case2: previous nesab not achieved and new acheived--> update start date of all active saving to be the saving date,
#consequently update deserve date to be 354 days later...update nesab date in zakah summary table
#case3: previous nesab achieved and new acheived(with entry deposite not ithdrawl)-->update start date of the current
#row to be saving date;consequently update deserve date to be 354 days later
#case4: previous nesab not achieved and new not acheived-->update start date and deserve date of all active rows to
#initial value...update nesab date in zakah summary table
            if nesab_acheived==False:
                if updatesummary_o.total_saving >= nesab:#old nesab False and new nesab True
                    updatesummary_o.nesab_day=updatedetails_o.saving_day
                    updatesummary_o.save()
                    for i in list_zakahdetails:
                        i.start_day=updatedetails_o.saving_day
                        i.deserve_day=updatedetails_o.saving_day+timedelta(days=354)
                        i.save()
            else:#old nesab check = True
                if updatesummary_o.total_saving > nesab:#neew nesab True
                    if updatedetails_o.active: #deposite not withdrawll
                        updatedetails_o.start_day=updatedetails_o.saving_day
                        updatedetails_o.deserve_day = updatedetails_o.saving_day + timedelta(days=354)
                        updatedetails_o.save()
                else:#old nesab True and new nesab False
                    updatesummary_o.nesab_day = date(1111,1,1)
                    updatesummary_o.save()
                    for i in list_zakahdetails:
                        i.start_day=date(1111,1,1)
                        i.deserve_day=date(1111,1,1)
                        i.save()

            return HttpResponseRedirect('/zakah1/profile')
        return render(request,'profile.html',{'name':user_name})
    request.session['mes']='Please sign in before accessing your profile page'#writing data in public container
    #  to be used by othe view functions
    return HttpResponseRedirect('/zakah1/signin')

########################################################################

########################################################################

def signout_f(request):
    logout(request)
    return HttpResponse('Successfuly logged out')
