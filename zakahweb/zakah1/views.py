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
    nesab=80000
    today_date=date.today()
    xz=date(2020,1,1)
    print type(xz), type(today_date)
    a=(today_date-xz).days
    print a , 'a'
    if request.user.is_authenticated():  # check user logged in
        full_name = request.user.get_full_name()
        user_name = request.user.username
        updatedetails_o = zakah_register_c()
        updatesummary_o = zakah_summary_c.objects.get(username=User.objects.get(username=user_name))
        set_zakahdetails = zakah_register_c.objects.filter(username=User.objects.get(username=user_name),
                                                            active=True)
        for i in set_zakahdetails:
            if i.deserve_day<=today_date and i.deserve_day>date(1111,1,1):
                difference_ratio=(today_date-i.start_day).days/354
                updatesummary_o.required_zakah=updatesummary_o.required_zakah+(i.zakah*difference_ratio)
                i.start_day=i.start_day+timedelta(days=(354*difference_ratio))
                i.deserve_day=i.start_day+timedelta(days=354)
        # creating list of zakah and deserve date to be diplayed in html table
        html_list = []
        if updatesummary_o.total_saving>=nesab:
            list_zakahdetails=sorted(set_zakahdetails,key=operator.attrgetter('deserve_day'),reverse=True)#transforms set to ordered list
            print list_zakahdetails[0].saving_day
            #adding all azkah of the same deserve date to be one item
            date1=timedelta(0)
            zakah1=0
            for i in list_zakahdetails:
                if date1==i.deserve_day:
                    zakah1=zakah1+i.zakah
                elif date1 != timedelta():
                    html_list.append({'date':date1, 'zakah': zakah1})
                    date1=i.deserve_day
                    zakah1=i.zakah
                else:
                    date1 = i.deserve_day
                    zakah1 = i.zakah
            html_list.append({'date':date1, 'zakah': zakah1})
        else:
            html_list = [{'date': "لا يوجد زكاة مستحقة", 'zakah': "لا يوجد زكاة مستحقة"}]
        return render(request, 'main_in.html', {'full_name':full_name,'mess':mess_main,'required_zakah':html_list})
    elif request.method=='POST':
        total_saving=request.POST['init_save_le']
        start_date=request.POST['init_save_date']
        if int(total_saving)<nesab:
            date_cell='غير مطلوب زكاة'
            zakah_cell='غير مطلوب زكاة'
        else:
            year, month = start_date.split('-')
            date_cell=date(int(year),int(month),1)+timedelta(days=354)
            zakah_cell=int(total_saving)*.025
        return render(request,'main_out2.html',{'date_cell':date_cell,'zakah_cell':zakah_cell,'start_date':start_date,'total_saving':total_saving})
    else:
        return render (request,'main_out1.html',{'mess':mess_main})

################################################################

################################################################
def signup_f(request):
    print 1010
    nesab=80000
    if not request.user.is_authenticated():
        print 1212
        if request.method=='POST':
            print 1313
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['password']
            firstname=request.POST['fname']
            lastname=request.POST['lname']
            total_saving_le=request.POST['init_save_le']
            saving_date=request.POST['init_save_date']
            year, month = saving_date.split('-')
            parsed_saving_date = datetime.date(int(year), int(month), 1)
            try:  # to check for username duplication error
                print 888888
                newuser =User.objects.create_user(username, email, password)
                newuser.first_name=firstname
                newuser.last_name=lastname
                print 999
                newuser.save()
                print 1111
                updatesummary_o = zakah_summary_c()
                updatesummary_o.username = User.objects.get(username=username)
                updatedetails_o = zakah_register_c()
                updatedetails_o.username = User.objects.get(username=username)
                if int(total_saving_le)>=nesab:
                    updatesummary_o.total_saving = total_saving_le
                    updatesummary_o.nesab_day = parsed_saving_date
                    updatesummary_o.required_zakah = 0
                    updatesummary_o.save()
                    updatedetails_o.saving_day = parsed_saving_date
                    updatedetails_o.saving=int(total_saving_le)
                    updatedetails_o.active_saving=updatedetails_o.saving
                    updatedetails_o.zakah=updatedetails_o.saving*.025
                    updatedetails_o.start_day=updatedetails_o.saving_day
                    updatedetails_o.deserve_day=updatedetails_o.saving_day+timedelta(days=354)
                    updatedetails_o.active=True
                    updatedetails_o.nesab_acheived=True
                    updatedetails_o.save()
                    print 7777777
                else:
                    updatesummary_o.total_saving = total_saving_le
                    updatesummary_o.nesab_day = date(1111,1,1)
                    updatesummary_o.required_zakah = 0
                    updatesummary_o.save()
                    updatedetails_o.saving_day = parsed_saving_date
                    updatedetails_o.saving = int(total_saving_le)
                    updatedetails_o.active_saving = updatedetails_o.saving
                    updatedetails_o.zakah = updatedetails_o.saving * .025
                    updatedetails_o.start_day = date(1111,1,1)
                    updatedetails_o.deserve_day = date(1111,1,1)
                    updatedetails_o.active = True
                    updatedetails_o.nesab_acheived=False
                    updatedetails_o.save()
                    print 44
                login(request,newuser)
                request.session['mes_main'] = 'تم انشاء حسابك و تسجيل بياناتك بنجاح'
                return HttpResponseRedirect(reverse('main'))
            except:
                print 141414
                request.session['mes_main'] = 'اسم المستخدم موجود بالفعل برجاء اختيار اسم اخر'
    else:
        print 15515
        request.session['mes_main'] = 'انت بالمفعل مسجل دخولك'
    print 177117
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
                res = authenticate(username=user_name, password=pass_word)
                if res is not None:
                    login(request, res)
                    return HttpResponseRedirect('/zakah1/main/')
                else:
                    request.session['mes_main']='اسم المستخدم او كلمة المرور غير صحيحة'
                    return HttpResponseRedirect(reverse('main'))
    else:
        print 666666
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
                previoue_nesab_achieved = False
            else:
                previoue_nesab_achieved = True
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
                set_zakahdetails = zakah_register_c.objects.filter(username=User.objects.get(username=user_name),
                    active=True)
                list_zakahdetails=sorted(set_zakahdetails, key=operator.attrgetter('saving_day'))#new
                n=len(list_zakahdetails)-1 #new#order of latest item
                print n,'haahaaaaaahaaaaaaaaaa'
                if updatedetails_o.saving_day<list_zakahdetails[n].saving_day or n==-1:
                    pass
                else:
                    net_save_icrease = saving_amount - updatesummary_o.total_saving
                    if net_save_icrease <= 0:
                        updatedetails_o.active_saving = 0
                        updatedetails_o.active = False
                    else:
                        updatedetails_o.active_saving = net_save_icrease
                    if updatedetails_o.saving<nesab:
                        updatedetails_o.nesab_acheived=False
                    else:
                        updatedetails_o.nesab_acheived=True

                    updatedetails_o.zakah = 0.025 * int(updatedetails_o.active_saving)
                    updatedetails_o.save()
                    #Now then all parameters of object of zakah register assigned initial values and saved
                    #the new object added to the table


                    ################################################################################################
                    # Values that need algorithms: Active zakah(any change of it requires change in zakah),Start date,Deserve date,and Active
                    ################################################################################################

                    ###############################################################################################
                    # if withdrawl deduct it from previous active saving one by one starting by latest saving date(consequently modify zakah)
                    # in same time if any active saving became 0 after deduction; modify 'active' to False, start and deserve dates to initial
                    if net_save_icrease < 0:
                        seq_deduct(net_save_icrease, set_zakahdetails)  # a function to execute the above description

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
                    updatesummary_o, updatedetails_o, list_zakahdetails = update_values_dates(previoue_nesab_achieved,
                                                                                                  updatedetails_o.nesab_acheived,
                                                                                                  updatesummary_o,
                                                                                                  updatedetails_o,
                                                                                                  set_zakahdetails)
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