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
import datetime, operator, time, copy
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
deduct_list=my_aux.list_deducted
net_deduct=my_aux.calc_net_deduc
copy_list=my_aux.list_copy


def main_f(request):
    mess_main=request.session.get('mes_main')
    request.session['mes_main']=''
    if mess_main==None:
        mess_main=''
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
        set_zakahdetails_all=zakah_register_c.objects.filter(username=User.objects.get(username=user_name))
        for i in set_zakahdetails:
            if i.deserve_day<=today_date and i.deserve_day>date(1111,1,1):
                difference_ratio=(today_date-i.start_day).days/354
                updatesummary_o.required_zakah=updatesummary_o.required_zakah+(i.zakah*difference_ratio)
                i.start_day=i.start_day+timedelta(days=(354*difference_ratio))
                i.deserve_day=i.start_day+timedelta(days=354)
        # creating list of zakah and deserve date to be diplayed in html table
        html_list = []
        list_zakahdetails = sorted(set_zakahdetails, key=operator.attrgetter('deserve_day'),
                                   reverse=True)  # transforms set to ordered list
        list_zakahdetails_all=sorted(set_zakahdetails_all, key=operator.attrgetter('saving_day'),reverse=True)
        if updatesummary_o.total_saving>=nesab:
            #adding all zkah of the same deserve date to be one item
            date1=timedelta(0)
            zakah1=0
            for i in list_zakahdetails:
                if i.deserve_day!=date(1111,1,1):
                    if date1==i.deserve_day:
                        zakah1=zakah1+i.zakah
                    elif date1 != timedelta():
                        html_list.append({'date':date1, 'zakah': zakah1})
                        date1=i.deserve_day
                        zakah1=i.zakah
                    else:
                        date1 = i.deserve_day
                        zakah1 = i.zakah
            if zakah1==0:
                html_list.append({'date':"لا يوجد زكاة مستحقة", 'zakah': "لا يوجد زكاة مستحقة"})
            else:
                html_list.append({'date':date1, 'zakah': zakah1})
        else:
            html_list = [{'date': "لا يوجد زكاة مستحقة", 'zakah': "لا يوجد زكاة مستحقة"}]
        html_history_list=[[i.saving_day,i.saving] for i in list_zakahdetails_all]
        print html_history_list,88888888888888888888
        print html_list,99999999999999999999
        return render(request, 'main_in.html', {'full_name':full_name,'mess':mess_main,'required_zakah':html_list,'saving_history':html_history_list})
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
                    updatedetails_o.net_save_increase=updatedetails_o.saving
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
        form_f = signin_form()#######################################################################

#######################################################################

    return HttpResponseRedirect(reverse('main'))


def update_DB_f(request):
    if request.user.is_authenticated():#check user logged in else redirect to signin with message
        user_name = request.user.username
        if request.method == 'POST':
            updatedetails_o = zakah_register_c()
            updatesummary_o = zakah_summary_c.objects.get(username=User.objects.get(username=user_name))
            nesab = 80000
            monthly_form = monthlysave_form(request.POST)
            # read data from html form
            if monthly_form.is_valid():
                saving_date = monthly_form.cleaned_data['month_save_date']
                saving_amount = monthly_form.cleaned_data['month_save_le']
                year, month = saving_date.split('-')
                parsed_saving_date = datetime.date(int(year), int(month), 1)

                ###############################################################################
                ### assign fixed values to object(username, saving, saving_day, nesab_acheived -- default values assigned through class inModels.py
                updatedetails_o.username = User.objects.get(username=user_name)
                updatedetails_o.saving_day = parsed_saving_date
                updatedetails_o.saving = float(saving_amount)
                # assign value of nesab_acheived
                if updatedetails_o.saving < nesab:
                    updatedetails_o.nesab_acheived = False
                else:
                    updatedetails_o.nesab_acheived = True
                nesab_acheived = updatedetails_o.nesab_acheived

                ##################################################################################
                ##assign other parameters to object(net_save_increase, active,active saving,zakah)--> then save to DB
                ##################################################################################

                #create a list of existing active items and existing all items(excluding the new item
                set_zakahdetails = zakah_register_c.objects.filter(username=User.objects.get(username=user_name),
                    active=True)
                list_zakahdetails=sorted(set_zakahdetails, key=operator.attrgetter('saving_day'))#new item not included
                set_zakahdetails_all=zakah_register_c.objects.filter(username=User.objects.get(username=user_name))
                list_zakahdetails_all=sorted(set_zakahdetails_all, key=operator.attrgetter('saving_day'))#ascending


                ##Creating the new list after adding the new item in place(either adding new or overriding existing item)
                # check if item already exists: override and keep its index
                override=False #initial value
                duplicate=False #initial value
                list_zakahdetails_all_1=[]#initial value
                new_item_index_all=0#initial value
                for old in list_zakahdetails_all:
                    if updatedetails_o.saving_day==old.saving_day:
                        override=True
                        print 'override=',override
                        if int(updatedetails_o.saving)==int(old.saving):
                            duplicate=True
                            print 'duplicate=',duplicate
                        else:
                            updatedetails_o.pk=old.pk
                            new_item_index_all=list_zakahdetails_all.index(old)
                            list_zakahdetails_all_1=copy.deepcopy(list_zakahdetails_all)
                            list_zakahdetails_all_1[new_item_index_all].saving=updatedetails_o.saving
                            list_zakahdetails_all_1[new_item_index_all].nesab_acheived= updatedetails_o.nesab_acheived
                            list_zakahdetails_all_1 = sorted(list_zakahdetails_all_1,
                                                            key=operator.attrgetter('saving_day'))#to be deleted
                            overrided_item=old
                            #if override and no duplicate create the new list(with the new item added and keep the old)
                        break
                if duplicate==False:#if duplicate(same savin_day and saving)-->skip all steps and go to 'return'
                    # if new item not exist add to the list and rearrange
                    print 'start_day', list_zakahdetails_all_1[new_item_index_all].start_day,'9009'
                    if not override:
                        print 'creat list_zakah_details_all_1 as no duplicate no override'
                        list_zakahdetails_all_1=copy.deepcopy(list_zakahdetails_all)
                        list_zakahdetails_all_1.append(updatedetails_o)
                        list_zakahdetails_all_1=sorted(list_zakahdetails_all_1,key=operator.attrgetter('saving_day'))
                        new_item_index_all=list_zakahdetails_all_1.index(updatedetails_o)

                    # getting value of new item index_all and new list_all length
                    length_list_all=len(list_zakahdetails_all_1)
                    # assign value of new item net_save_increase and old_net_save_increase and -if applicable- the next item net_save_increase
                    if new_item_index_all==0:
                        print 'new item index = 0'
                        old_net_save_increase=0
                        net_save_increase=updatedetails_o.saving
                        list_zakahdetails_all_1[new_item_index_all].net_save_increase=net_save_increase
                    else:
                        old_net_save_increase = list_zakahdetails_all_1[new_item_index_all-1].net_save_increase
                        net_save_increase = list_zakahdetails_all_1[new_item_index_all].saving-list_zakahdetails_all_1[new_item_index_all-1].saving
                        print 'n s e', net_save_increase
                        list_zakahdetails_all_1[new_item_index_all].net_save_increase = net_save_increase
                    # assign value of next item net_save_increase(if not the last item in the list)
                    if new_item_index_all<length_list_all-1:
                        print 'new item index is not the first nor the last'
                        list_zakahdetails_all_1[new_item_index_all + 1].net_save_increase=77777#to be deleted
                        list_zakahdetails_all_1[new_item_index_all + 1].net_save_increase=list_zakahdetails_all_1[new_item_index_all+1].saving-list_zakahdetails_all_1[new_item_index_all].saving
########################################################################################################################
# So far: Old and new list_all created and arranged ascendig
#         Only old(not new) list created and arranged acending
#         username, saving, saving_day, nesab_acheived, and net_save_increase(of new item, and next and previous items if applicable) assigned
# still need to assign: start_day(consequently deserve_day), active_saving(consequenty zakah and active)

                    # assign values of previous_nesab_acheived
                    if new_item_index_all==0:
                        previous_nesab_acheived=False
                    else:
                        previous_nesab_acheived = list_zakahdetails_all_1[new_item_index_all - 1].nesab_acheived
                    if override:
                        old_nesab_acheived=old.nesab_acheived# from the previous for loop

                    ################################################


                    #assign value of active(default=True) and active_saving(initial values to be changed in case new item is not the latest)
                    print 'nse', net_save_increase
                    if net_save_increase <= 0:
                        list_zakahdetails_all_1[new_item_index_all].active_saving = 0
                        list_zakahdetails_all_1[new_item_index_all].active = False
                    else:
                        list_zakahdetails_all_1[new_item_index_all].active_saving = net_save_increase

                    list_zakahdetails_all_1[new_item_index_all].zakah = 0.025 * int(list_zakahdetails_all_1[new_item_index_all].active_saving)
                    list_zakahdetails_all_1[new_item_index_all].active=True
                    list_zakahdetails_all_1[new_item_index_all].save()

                    ###################################################################################################
                    if new_item_index_all==0:
                        if not override:
                            if list_zakahdetails_all_1[0].net_save_increase>=list_zakahdetails_all[0].active_saving:
                                list_zakahdetails_all_1[0].active_saving=list_zakahdetails_all[0].active_saving
                                list_zakahdetails_all_1[1].active_saving=0
                            else:
                                list_zakahdetails_all_1[0].active_saving=list_zakahdetails_all_1[0].net_save_increase
                                list_zakahdetails_all_1[1].active_saving=list_zakahdetails_all[0].active_saving-list_zakahdetails_all_1[0].net_save_increase
                            if list_zakahdetails_all_1[0].active_saving==0:
                                list_zakahdetails_all_1[0].active=False
                                list_zakahdetails_all_1[0].zakah=0
                            else:
                                list_zakahdetails_all_1[0].active = True
                                list_zakahdetails_all_1[0].zakah = 0.025 * list_zakahdetails_all_1[0].active_saving
                            #assign values of active_saving and active for first item
                            if list_zakahdetails_all_1[1].active_saving==0:
                                list_zakahdetails_all_1[1].active=False
                                list_zakahdetails_all_1[1].zakah=0
                                list_zakahdetails_all_1[1].start_day = date(1111, 1, 1)
                                list_zakahdetails_all_1[1].deserve_day = date(1111, 1, 1)
                            else:
                                list_zakahdetails_all_1[1].active = True
                                list_zakahdetails_all_1[1].zakah = 0.025 * list_zakahdetails_all_1[0].active_saving
                            list_zakahdetails_all_1[1].save()
                        else:#if override
                            if len(list_zakahdetails_all_1)>1:#list has more than 1 item
                                total_active_saving_0=list_zakahdetails_all[0].active_saving+list_zakahdetails_all[1].active_saving
                                if list_zakahdetails_all_1[0].net_save_increase >= total_active_saving_0:
                                    list_zakahdetails_all_1[0].active_saving = total_active_saving_0
                                    list_zakahdetails_all_1[1].active_saving = 0
                                else:
                                    list_zakahdetails_all_1[0].active_saving = list_zakahdetails_all_1[0].net_save_increase
                                    list_zakahdetails_all_1[1].active_saving = total_active_saving_0-list_zakahdetails_all_1[0].net_save_increase
                                if list_zakahdetails_all_1[0].active_saving == 0:
                                    list_zakahdetails_all_1[0].active = False
                                    list_zakahdetails_all_1[0].zakah = 0
                                else:
                                    list_zakahdetails_all_1[0].active = True
                                    list_zakahdetails_all_1[0].zakah = 0.025 * list_zakahdetails_all_1[0].active_saving
                                # assign values of active_saving and active for first item
                                if list_zakahdetails_all_1[1].active_saving == 0:
                                    list_zakahdetails_all_1[1].active = False
                                    list_zakahdetails_all_1[1].zakah = 0
                                    list_zakahdetails_all_1[1].start_day = date(1111, 1, 1)
                                    list_zakahdetails_all_1[1].deserve_day = date(1111, 1, 1)
                                else:
                                    list_zakahdetails_all_1[1].active = True
                                    list_zakahdetails_all_1[1].zakah = 0.025 * list_zakahdetails_all_1[0].active_saving
                                list_zakahdetails_all_1[1].save()

                            else:#list has only 1 item
                                list_zakahdetails_all_1[0].active_saving = list_zakahdetails_all_1[0].net_save_increase
                                if list_zakahdetails_all_1[0].active_saving == 0:
                                    list_zakahdetails_all_1[0].active = False
                                    list_zakahdetails_all_1[0].zakah = 0
                                else:
                                    list_zakahdetails_all_1[0].active = True
                                    list_zakahdetails_all_1[0].zakah = 0.025 * list_zakahdetails_all_1[0].active_saving

                        ##assign values for start_day and deserve_day of the current item
                        list_zakahdetails_1 = []
                        # create list_zakahdetails_1 which contains all active items excluding the latest item
                        for i in list_zakahdetails_all_1:
                            if i.active:
                                list_zakahdetails_1 += [i]
                        #assign values of dates
                        if length_list_all>1:
                            if nesab_acheived and list_zakahdetails_1[1].start_day==list_zakahdetails_1[1].saving_day:
                                list_zakahdetails_all_1[0].start_day=list_zakahdetails_all_1[0].saving_day
                                list_zakahdetails_all_1[0].deserve_day = list_zakahdetails_all_1[0].saving_day+timedelta(days=354)
                            elif list_zakahdetails_all_1[0].active:
                                list_zakahdetails_all_1[0].start_day = list_zakahdetails_1[1].start_day
                                list_zakahdetails_all_1[0].deserve_day = list_zakahdetails_1[1].deserve_day
                            else:
                                list_zakahdetails_all_1[0].start_day = date(1111,1,1)
                                list_zakahdetails_all_1[0].deserve_day = date(1111,1,1)
                        elif nesab_acheived:#new item is the only item and nesab_acheived
                            list_zakahdetails_all_1[0].start_day = list_zakahdetails_all_1[0].saving_day
                            list_zakahdetails_all_1[0].deserve_day = list_zakahdetails_all_1[0].saving_day + timedelta(
                                days=354)
                        else:#new item is the only item and not nesab_acheived
                            list_zakahdetails_all_1[0].start_day = date(1111, 1, 1)
                            list_zakahdetails_all_1[0].deserve_day = date(1111, 1, 1)
                        list_zakahdetails_all_1[0].save()

                    elif new_item_index_all<length_list_all-1:#new item not the latest item saving date
                        #update the next item net_save_increase
                        list_zakahdetails_all_1[new_item_index_all+1].net_save_increase=list_zakahdetails_all_1[new_item_index_all+1].saving-list_zakahdetails_all_1[new_item_index_all].saving
                        list_zakahdetails_all_1[new_item_index_all+1].save()
                        # assign value of next_nesab_acheived if older date
                        #update old active_saving, active, and zakah
                        ################################################################
                        #update/assign active_saving, acive, and zakah
                        if override:
                            print 'start_day',list_zakahdetails_all_1[new_item_index_all].start_day
                            print 'inside if override'
                            total_active_saving = list_zakahdetails_all[new_item_index_all].active_saving + \
                                                  list_zakahdetails_all[new_item_index_all + 1].active_saving

                            case1=overrided_item.net_save_increase>0 and list_zakahdetails_all_1[new_item_index_all+1].saving>list_zakahdetails_all_1[new_item_index_all].saving and list_zakahdetails_all_1[new_item_index_all].net_save_increase<0
                            case2=overrided_item.net_save_increase<0 and overrided_item.saving<list_zakahdetails_all_1[new_item_index_all+1].saving
                            case3=overrided_item.net_save_increase<0 and overrided_item.saving>list_zakahdetails_all_1[new_item_index_all+1].saving and list_zakahdetails_all_1[new_item_index_all].saving<list_zakahdetails_all_1[new_item_index_all+1].saving
                            if case1 or case2 or case3:
                                print 'case1=',case1
                                print 'case2=',case2
                                print 'case3=',case3
                                upper_deduct=net_deduct(list_zakahdetails_all[new_item_index_all:])
                                print 'upper_deduct', upper_deduct
                                deduction_list=deduct_list(list_zakahdetails_all_1[:new_item_index_all],upper_deduct)
                                print 'deduction list', deduction_list
                                abs_upper_deduct=abs(upper_deduct)
                                for i in deduction_list:
                                    print'inside return deducted loop'
                                    index=list_zakahdetails_all_1.index(i[0])
                                    print 'item before', list_zakahdetails_all_1[index].saving_day,list_zakahdetails_all_1[index].active_saving
                                    list_zakahdetails_all_1[index].active_saving+=i[1]
                                    if list_zakahdetails_all_1[index].active_saving>0:
                                        list_zakahdetails_all_1[index].active=True
                                    else:
                                        list_zakahdetails_all_1[index].active=False
                                    list_zakahdetails_all_1[index].zakah=.025*list_zakahdetails_all_1[index].active_saving
                                    list_zakahdetails_all_1[index].save()
                                    print 'item after', list_zakahdetails_all_1[index].saving_day,list_zakahdetails_all_1[index].active_saving

                                print '1 list_zakahdetails_all_1[new_item_index_all-1].active_saving=', list_zakahdetails_all_1[new_item_index_all-1].active_saving
                                #calculate the new active_saving of new_item_index_all+1
                                if list_zakahdetails_all_1[new_item_index_all+1].net_save_increase<=0 or abs(net_deduct(list_zakahdetails_all_1[new_item_index_all+2:]))>list_zakahdetails_all_1[new_item_index_all+1].net_save_increase:
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=0
                                    print 'if 1'
                                elif len(list_zakahdetails_all_1)==new_item_index_all+2:
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=list_zakahdetails_all_1[new_item_index_all+1].net_save_increase
                                    print 'if 2'
                                else:
                                    print 'if 3'
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=list_zakahdetails_all_1[new_item_index_all+1].net_save_increase+net_deduct(list_zakahdetails_all_1[new_item_index_all+2:])
                                if list_zakahdetails_all_1[new_item_index_all+1].active_saving==0:
                                    list_zakahdetails_all_1[new_item_index_all+1].active=False
                                    list_zakahdetails_all_1[new_item_index_all+1].zakah=0
                                else:
                                    list_zakahdetails_all_1[new_item_index_all + 1].active = True
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah = 0.025*list_zakahdetails_all_1[new_item_index_all+1].active_saving
                                list_zakahdetails_all_1[new_item_index_all+1].save()

                                upper_deduct_1=net_deduct(list_zakahdetails_all_1[new_item_index_all+1:])
                                print 'upper_deduct_1',upper_deduct_1
                                print '2 list_zakahdetails_all_1[new_item_index_all-1].active_saving=', list_zakahdetails_all_1[new_item_index_all-1].active_saving
                                if list_zakahdetails_all_1[new_item_index_all].net_save_increase<0:
                                    total_deduct=upper_deduct_1+list_zakahdetails_all_1[new_item_index_all].net_save_increase
                                    print 'list_zakahdetails_all_1[new_item_index_all].net_save_increase=',list_zakahdetails_all_1[new_item_index_all].net_save_increase
                                    print 'total deduct=',total_deduct
                                    seq_deduct(total_deduct,list_zakahdetails_all_1[:new_item_index_all])
                                    print '3 list_zakahdetails_all_1[new_item_index_all-1].active_saving=', \
                                        list_zakahdetails_all_1[new_item_index_all - 1].active_saving
                                else:
                                    seq_deduct(upper_deduct_1,list_zakahdetails_all_1[:new_item_index_all+1])
                                    print '4 list_zakahdetails_all_1[new_item_index_all-1].active_saving=', \
                                    list_zakahdetails_all_1[new_item_index_all - 1].active_saving

                            else:
                                if total_active_saving>list_zakahdetails_all_1[new_item_index_all].net_save_increase:
                                    print 'inside else case1/2/3-1'
                                    list_zakahdetails_all_1[new_item_index_all].active_saving=list_zakahdetails_all_1[new_item_index_all].net_save_increase
                                    list_zakahdetails_all_1[new_item_index_all].zakah =.025*int(list_zakahdetails_all_1[new_item_index_all].active_saving)
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=total_active_saving-list_zakahdetails_all_1[new_item_index_all].active_saving
                                    list_zakahdetails_all_1[new_item_index_all+1].zakah =.025*int(list_zakahdetails_all_1[new_item_index_all+1].active_saving)
                                else:
                                    print 'inside else case1/2/3-2'
                                    list_zakahdetails_all_1[new_item_index_all].active_saving=total_active_saving
                                    list_zakahdetails_all_1[new_item_index_all].zakah =.025*int(list_zakahdetails_all_1[new_item_index_all].active_saving)
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=0
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah =0
                                if list_zakahdetails_all_1[new_item_index_all].net_save_increase<=0 or list_zakahdetails_all_1[new_item_index_all].active_saving==0:
                                    print 'inside else case1/2/3-3'
                                    list_zakahdetails_all_1[new_item_index_all].active_saving=0
                                    list_zakahdetails_all_1[new_item_index_all].active=False
                                    list_zakahdetails_all_1[new_item_index_all].zakah=0
                                if list_zakahdetails_all_1[new_item_index_all+1].net_save_increase<=0 or list_zakahdetails_all_1[new_item_index_all+1].active_saving==0:
                                    print 'inside else case1/2/3-4'
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving=0
                                    list_zakahdetails_all_1[new_item_index_all+1].active=False
                                    list_zakahdetails_all_1[new_item_index_all+1].zakah=0
                                list_zakahdetails_all_1[new_item_index_all].save()
                                list_zakahdetails_all_1[new_item_index_all+1].save()
                        else:#in case no override
                            print 'ab1'
                            print 'list_zakahdetails_all_1[new_item_index_all+1].saving', list_zakahdetails_all_1[new_item_index_all+1].saving
                            print 'list_zakahdetails_all_1[new_item_index_all-1].saving', list_zakahdetails_all_1[new_item_index_all-1].saving
                            #if list_zakahdetails_all_1[new_item_index_all+1].saving>list_zakahdetails_all_1[new_item_index_all].saving:
                            print 'ab2'
                            if list_zakahdetails_all_1[new_item_index_all].net_save_increase<0:
                                print 'ab3'
                                list_zakahdetails_all_1[new_item_index_all].active_saving =0
                                list_zakahdetails_all_1[new_item_index_all].active=False
                                list_zakahdetails_all_1[new_item_index_all].zakah=0

                                deduct_f=0#initial value
                            if list_zakahdetails_all_1[new_item_index_all + 1].saving >list_zakahdetails_all_1[new_item_index_all-1].saving and net_save_increase<0:
                                print 'ab4'
                                if len(list_zakahdetails_all_1) < new_item_index_all + 3:
                                    upper_deduct = 0
                                else:
                                    upper_deduct = net_deduct(list_zakahdetails_all_1[new_item_index_all + 1:])
                                if upper_deduct==0:
                                    list_zakahdetails_all_1[new_item_index_all + 1].active_saving+=abs(net_save_increase)
                                    list_zakahdetails_all_1[new_item_index_all + 1].active = True
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah =.025*int(list_zakahdetails_all_1[new_item_index_all + 1].active_saving)
                                    deduct_f=net_save_increase
                                elif abs(upper_deduct)>=abs(net_save_increase):
                                    list_zakahdetails_all_1[new_item_index_all + 1].active_saving = 0
                                    list_zakahdetails_all_1[new_item_index_all + 1].active = False
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah = 0
                                else:
                                    deduct_f = abs(upper_deduct) - abs(net_save_increase)
                                    list_zakahdetails_all_1[new_item_index_all + 1].active_saving+= abs(
                                        deduct_f)
                                    list_zakahdetails_all_1[new_item_index_all + 1].active = True
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah = .025*int(list_zakahdetails_all_1[new_item_index_all + 1].active_saving)
                                remain_deduct = seq_deduct(deduct_f, list_zakahdetails_all_1[:new_item_index_all])
                                list_zakahdetails_all_1[new_item_index_all].save()
                                list_zakahdetails_all_1[new_item_index_all + 1].save()
                                print remain_deduct
                            elif list_zakahdetails_all_1[new_item_index_all+1].saving>list_zakahdetails_all_1[new_item_index_all].saving and net_save_increase<0:
                                print 'ab5'
                                if len(list_zakahdetails_all_1) < new_item_index_all + 3:
                                    upper_deduct = 0
                                else:
                                    upper_deduct = net_deduct(list_zakahdetails_all_1[new_item_index_all + 2:])
                                print upper_deduct

                                if abs(upper_deduct)>=abs(list_zakahdetails_all_1[new_item_index_all+1].net_save_increase):
                                    deduct_f=list_zakahdetails_all_1[new_item_index_all+1].net_save_increase-list_zakahdetails_all_1[new_item_index_all+1].net_save_increase
                                    list_zakahdetails_all_1[new_item_index_all + 1].active_saving=0
                                    list_zakahdetails_all_1[new_item_index_all + 1].active=False
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah=0
                                    print deduct_f,1234
                                else:
                                    deduct_f=abs(upper_deduct)-abs(list_zakahdetails_all_1[new_item_index_all+1].net_save_increase)
                                    list_zakahdetails_all_1[new_item_index_all + 1].active_saving = abs(deduct_f)
                                    list_zakahdetails_all_1[new_item_index_all + 1].active = True
                                    list_zakahdetails_all_1[new_item_index_all + 1].zakah = .025*int(list_zakahdetails_all_1[new_item_index_all + 1].active_saving)
                                    print deduct_f,4321
                                remain_deduct=seq_deduct(deduct_f,list_zakahdetails_all_1[:new_item_index_all])
                                print remain_deduct

                                list_zakahdetails_all_1[new_item_index_all].save()
                                list_zakahdetails_all_1[new_item_index_all+1].save()
                            elif list_zakahdetails_all_1[new_item_index_all+1].active_saving<list_zakahdetails_all_1[new_item_index_all].active_saving:
                                list_zakahdetails_all_1[new_item_index_all].active_saving=list_zakahdetails_all_1[new_item_index_all+1].active_saving
                                if list_zakahdetails_all_1[new_item_index_all].active_saving==0:
                                    list_zakahdetails_all_1[new_item_index_all].active=False
                                list_zakahdetails_all_1[new_item_index_all].zakah=.025*int(list_zakahdetails_all_1[new_item_index_all].active_saving)
                                list_zakahdetails_all_1[new_item_index_all+1].active_saving=0
                                list_zakahdetails_all_1[new_item_index_all+1].active=False
                                list_zakahdetails_all_1[new_item_index_all+1].zakah=0
                                list_zakahdetails_all_1[new_item_index_all].save()
                                list_zakahdetails_all_1[new_item_index_all+1].save()
                            else:
                                list_zakahdetails_all_1[new_item_index_all+1].active_saving =list_zakahdetails_all_1[new_item_index_all+1].active_saving-list_zakahdetails_all_1[new_item_index_all].active_saving
                                list_zakahdetails_all_1[new_item_index_all+1].zakah = .025 * int(
                                    list_zakahdetails_all_1[new_item_index_all+1].active_saving)
                                list_zakahdetails_all_1[new_item_index_all+1].save()
                #####################################################################################################################
                        #new item is neither the first nor the last item
                ######################################################################################################################
                        #assign start_day and desreve_day for the new and update the old if needed
                        # create list_zakahdetails_1 which contains all 'active' items excluding the latest item

                    ################################################################################################################
                        list_zakahdetails_1=[]#inital value
                        for i in list_zakahdetails_all_1:
                            if i.active:
                              list_zakahdetails_1+=[i]

                        noreset=True#initial value
                        for i in list_zakahdetails_all_1[new_item_index_all+1:]:
                            if i.active:
                                break
                            elif not i.nesab_acheived:
                                noreset=False
                                break

                        if list_zakahdetails_1[-1].saving_day>list_zakahdetails_all_1[new_item_index_all].saving_day:#if new item is not the last active item
                            for i in list_zakahdetails_1:#get value of next_active_item_index
                                if i.saving_day > list_zakahdetails_all_1[new_item_index_all].saving_day:
                                    next_active_item_index = list_zakahdetails_1.index(i)
                                    break
                            if not override:
                                if previous_nesab_acheived and nesab_acheived and noreset and list_zakahdetails_1[next_active_item_index].start_day==list_zakahdetails_1[next_active_item_index].saving_day:
                                    list_zakahdetails_all_1[new_item_index_all].start_day = list_zakahdetails_all_1[
                                        new_item_index_all ].saving_day
                                    list_zakahdetails_all_1[new_item_index_all].deserve_day = list_zakahdetails_all_1[
                                        new_item_index_all].saving_day+timedelta(days=354)
                                    list_zakahdetails_all_1[new_item_index_all].save()
                                elif previous_nesab_acheived and not nesab_acheived and noreset and list_zakahdetails_1[next_active_item_index].start_day==list_zakahdetails_1[next_active_item_index].saving_day:
                                    for i in list_zakahdetails_all_1[:new_item_index_all+1]:
                                        if i.active:
                                            i.start_day=list_zakahdetails_1[next_active_item_index].start_day
                                            i.deserve_day=list_zakahdetails_1[next_active_item_index].deserve_day
                                            i.save()
                                elif not previous_nesab_acheived and nesab_acheived and noreset and list_zakahdetails_1[next_active_item_index].start_day==list_zakahdetails_1[next_active_item_index].saving_day:
                                    for i in list_zakahdetails_all_1[:new_item_index_all+1]:
                                        if i.active:
                                            i.start_day=list_zakahdetails_all_1[new_item_index_all].saving_day
                                            i.deserve_day=list_zakahdetails_all_1[new_item_index_all].saving_day+timedelta(days=354)
                                            i.save()
                                else:
                                    list_zakahdetails_all_1[new_item_index_all].start_day =list_zakahdetails_1[next_active_item_index].start_day
                                    list_zakahdetails_all_1[new_item_index_all].deserve_day = list_zakahdetails_1[next_active_item_index].deserve_day
                                    list_zakahdetails_all_1[new_item_index_all].save()
                                list_zakahdetails_all_1[new_item_index_all + 1].save()
                            else:#if override
                                print 'el1',list_zakahdetails_all_1[new_item_index_all].start_day
                                if noreset and list_zakahdetails_1[next_active_item_index].start_day==list_zakahdetails_1[next_active_item_index].saving_day:
                                    print 'el2'
                                    if not previous_nesab_acheived:
                                        if not old_nesab_acheived and nesab_acheived:
                                            for i in list_zakahdetails_all_1[:new_item_index_all + 1]:
                                                if i.active:
                                                    i.start_day = list_zakahdetails_all_1[new_item_index_all].saving_day
                                                    i.deserve_day = list_zakahdetails_all_1[
                                                                        new_item_index_all].saving_day + timedelta(
                                                        days=354)
                                                    i.save()
                                        elif old_nesab_acheived and not nesab_acheived:
                                            for i in list_zakahdetails_all_1[:new_item_index_all + 1]:
                                                if i.active:
                                                    i.start_day = list_zakahdetails_1[next_active_item_index].start_day
                                                    i.deserve_day = list_zakahdetails_1[
                                                        next_active_item_index].deserve_day
                                                    i.save()
                                    else:#previous_nesab_acheived
                                        print 'el3'
                                        if old_nesab_acheived and not nesab_acheived:
                                            for i in list_zakahdetails_all_1[:new_item_index_all + 1]:
                                                print 'el4'
                                                if i.active:
                                                    i.start_day = list_zakahdetails_1[next_active_item_index].start_day
                                                    i.deserve_day = list_zakahdetails_1[
                                                        next_active_item_index].deserve_day
                                                    i.save()
                                        elif not old_nesab_acheived and nesab_acheived:
                                            print 'el5'
                                            list_zakahdetails_all_1[new_item_index_all].start_day = \
                                            list_zakahdetails_all_1[
                                                new_item_index_all].saving_day
                                            list_zakahdetails_all_1[new_item_index_all].deserve_day = \
                                            list_zakahdetails_all_1[
                                                new_item_index_all].saving_day + timedelta(days=354)
                                            list_zakahdetails_all_1[new_item_index_all].save()
                                            x=range(0,new_item_index_all)
                                            x.reverse()
                                            date_o=list_zakahdetails_all_1[new_item_index_all].saving_day
                                            sw = False
                                            for i in x:#update previous items(they were affected by old item)
                                                if list_zakahdetails_all_1[i].nesab_acheived and not sw:
                                                    if list_zakahdetails_all_1[i].active:
                                                        date_o=list_zakahdetails_all_1[i].saving_day
                                                        list_zakahdetails_all_1[i].start_day=list_zakahdetails_all_1[i].saving_day
                                                        list_zakahdetails_all_1[i].deserve_day=list_zakahdetails_all_1[i].saving_day+timedelta(days=354)
                                                        list_zakahdetails_all_1[i].save()
                                                else:
                                                    sw=True
                                                    if list_zakahdetails_all_1[i].active:
                                                        list_zakahdetails_all_1[i].start_day=date_o
                                                        list_zakahdetails_all_1[i].deserve_day=date_o+timedelta(days=354)
                                                        list_zakahdetails_all_1[i].save()
                        else:#if the new item has no active item next
                            if not override:
                                if previous_nesab_acheived and nesab_acheived and list_zakahdetails_all_1[-1].nesab_acheived:
                                    list_zakahdetails_all_1[new_item_index_all].start_day=list_zakahdetails_all_1[new_item_index_all].saving_day
                                    list_zakahdetails_all_1[new_item_index_all].deserve_day = list_zakahdetails_all_1[
                                        new_item_index_all].saving_day+timedelta(days=354)
                                elif not previous_nesab_acheived and nesab_acheived and list_zakahdetails_all_1[-1].nesab_acheived:
                                    for i in list_zakahdetails_all_1[:new_item_index_all + 1]:
                                        if i.active:
                                            i.start_day = list_zakahdetails_all_1[new_item_index_all].saving_day
                                            i.deserve_day = list_zakahdetails_all_1[
                                                                new_item_index_all].saving_day + timedelta(
                                                days=354)
                                            i.save()
                            else:#if override
                                if previous_nesab_acheived and not old_nesab_acheived and nesab_acheived and list_zakahdetails_all_1[-1].nesab_acheived:
                                    list_zakahdetails_all_1[new_item_index_all].start_day = \
                                        list_zakahdetails_all_1[
                                            new_item_index_all].saving_day
                                    list_zakahdetails_all_1[new_item_index_all].deserve_day = \
                                        list_zakahdetails_all_1[
                                            new_item_index_all].saving_day + timedelta(days=354)
                                    list_zakahdetails_all_1[new_item_index_all].save()
                                    x = range(0, new_item_index_all)
                                    x.reverse()
                                    date_o = list_zakahdetails_all_1[new_item_index_all].saving_day
                                    sw = False
                                    for i in x:  # update previous items(they were affected by old item)
                                        if list_zakahdetails_all_1[i].nesab_acheived and not sw:
                                            if list_zakahdetails_all_1[i].active:
                                                date_o = list_zakahdetails_all_1[i].saving_day
                                                list_zakahdetails_all_1[i].start_day = list_zakahdetails_all_1[
                                                    i].saving_day
                                                list_zakahdetails_all_1[i].deserve_day = list_zakahdetails_all_1[
                                                                                             i].saving_day + timedelta(
                                                    days=354)
                                                list_zakahdetails_all_1[i].save()
                                        else:
                                            sw = True
                                            if list_zakahdetails_all_1[i].active:
                                                list_zakahdetails_all_1[i].start_day = date_o
                                                list_zakahdetails_all_1[i].deserve_day = date_o + timedelta(days=354)
                                                list_zakahdetails_all_1[i].save()
                                elif not previous_nesab_acheived and not old_nesab_acheived and nesab_acheived and list_zakahdetails_all_1[-1].nesab_acheived:
                                    for i in list_zakahdetails_all_1[:new_item_index_all + 1]:
                                        if i.active:
                                            i.start_day = list_zakahdetails_all_1[new_item_index_all].saving_day
                                            i.deserve_day = list_zakahdetails_all_1[
                                                                new_item_index_all].saving_day + timedelta(
                                                days=354)
                                            i.save()


                    ####################################################################################################

                    else:# new item is the last item
                        #Now then all parameters of object of zakah register assigned initial values and saved
                        #the new object added to the table
                        list_zakahdetails_1=[]
                        #create list_zakahdetails_1 which contains all active items excluding the latest item
                        for i in list_zakahdetails_all_1:
                            if i.active:
                                list_zakahdetails_1+=[i]
                        if list_zakahdetails_all_1[-1].active:
                            list_zakahdetails_1.pop()

                        ################################################################################################
                        # Values that need algorithms: Active zakah(any change of it requires change in zakah),Start date,Deserve date,and Active
                        ################################################################################################

                        ###############################################################################################
                        # if withdrawl deduct it from previous active saving one by one starting by latest saving date(consequently modify zakah)
                        # in same time if any active saving became 0 after deduction; modify 'active' to False, start and deserve dates to initial
                        print 'a1'
                        if override:#if override the last item
                            print 'a2'
                            if list_zakahdetails_all[-1].net_save_increase>=0 and net_save_increase<0:#old no deduct and new deduct
                                print 'a2-1'
                                seq_deduct(net_save_increase, list_zakahdetails_1)
                            elif list_zakahdetails_all[-1].net_save_increase<0:#old deduct
                                print 'a2-2'
                                if net_save_increase<list_zakahdetails_all[-1].net_save_increase:#new deduct more
                                    print 'a2-2-1'
                                    seq_deduct(net_save_increase-list_zakahdetails_all[-1].net_save_increase, list_zakahdetails_1)
                                else:#new deduct less or no deduct#to use the add function then deduct or not as required
                                    print 'a2-2-2'
                                    net_deduct_1=list_zakahdetails_all[-1].net_save_increase
                                    deduction_list = deduct_list(list_zakahdetails_all_1[:new_item_index_all],
                                                                 net_deduct_1)
                                    print 'deduction list_1', deduction_list
                                    for i in deduction_list:
                                        print'inside return deducted loop_1'
                                        index = list_zakahdetails_all_1.index(i[0])
                                        print 'item before_1', list_zakahdetails_all_1[index].saving_day, \
                                        list_zakahdetails_all_1[index].active_saving
                                        list_zakahdetails_all_1[index].active_saving += i[1]
                                        if list_zakahdetails_all_1[index].active_saving > 0:
                                            list_zakahdetails_all_1[index].active = True
                                        else:
                                            list_zakahdetails_all_1[index].active = False
                                        list_zakahdetails_all_1[index].zakah = .025 * list_zakahdetails_all_1[
                                            index].active_saving
                                        list_zakahdetails_all_1[index].save()
                                        print 'item after_1', list_zakahdetails_all_1[index].saving_day, \
                                        list_zakahdetails_all_1[index].active_saving
                                    if net_save_increase<0:
                                        seq_deduct(net_save_increase, list_zakahdetails_all_1[:new_item_index_all])


                        else:#without override
                            print 'a3'
                            if net_save_increase < 0:
                                print 'list_zakahdetails_1',list_zakahdetails_1,'net save increase', net_save_increase
                                seq_deduct(net_save_increase, list_zakahdetails_1)  # a function to execute the above description


                            # case1: previous nesab not achieved and new not acheived-->No change; keep start and deserve dates with initial values
                                # assign start and deserve dates based on previous and current 'nesab acheived' status
                                # first update total saving in 'zakah summary' table

                                # case2: previous nesab not achieved and new acheived--> update start date of all active saving to be the saving date,
                            # consequently update deserve date to be 354 days later...update nesab date in zakah summary table
                            # case3: previous nesab achieved and new acheived(with entry deposite not ithdrawl)-->update start date of the current
                            # row to be saving date;consequently update deserve date to be 354 days later
                            # case4: previous nesab not achieved and new not acheived-->update start date and deserve date of all active rows to
                            # initial value...update nesab date in zakah summary table
                        if not override:
                            updatesummary_o, list_zakahdetails_all_1[-1], list_zakahdetails_1 = update_values_dates(previous_nesab_acheived,
                                                                                                      nesab_acheived,
                                                                                                      updatesummary_o,
                                                                                                                        list_zakahdetails_all_1[
                                                                                                                            -1],
                                                                                                      list_zakahdetails_1)
                        else:#last item overrided
                            print 'last override', list_zakahdetails_all_1[new_item_index_all].start_day
                            if previous_nesab_acheived:
                                if old_nesab_acheived and not nesab_acheived:
                                    for i in list_zakahdetails_all_1:
                                        if i.active:
                                            i.start_day=date(1111,1,1)
                                            i.deserve_day=date(1111,1,1)
                                            i.save()
                                elif not old_nesab_acheived and nesab_acheived:
                                    print 'last elif 222'
                                    list_zakahdetails_all_1[new_item_index_all].start_day = \
                                        list_zakahdetails_all_1[
                                            new_item_index_all].saving_day
                                    list_zakahdetails_all_1[new_item_index_all].deserve_day = \
                                        list_zakahdetails_all_1[
                                            new_item_index_all].saving_day + timedelta(days=354)
                                    list_zakahdetails_all_1[new_item_index_all].nesab_acheived=True
                                    list_zakahdetails_all_1[new_item_index_all].save()
                                    x = range(0, new_item_index_all)
                                    x.reverse()
                                    date_o = list_zakahdetails_all_1[new_item_index_all].saving_day
                                    sw = False
                                    for i in x:  # update previous items(they were affected by old item)
                                        if list_zakahdetails_all_1[i].nesab_acheived and not sw:
                                            if list_zakahdetails_all_1[i].active:
                                                date_o = list_zakahdetails_all_1[i].saving_day
                                                list_zakahdetails_all_1[i].start_day = list_zakahdetails_all_1[
                                                    i].saving_day
                                                list_zakahdetails_all_1[i].deserve_day = list_zakahdetails_all_1[
                                                                                             i].saving_day + timedelta(
                                                    days=354)
                                                list_zakahdetails_all_1[i].save()
                                        else:
                                            sw = True
                                            if list_zakahdetails_all_1[i].active:
                                                list_zakahdetails_all_1[i].start_day = date_o
                                                list_zakahdetails_all_1[i].deserve_day = date_o + timedelta(days=354)
                                                list_zakahdetails_all_1[i].save()
                            else:#previous_nesab not acheived
                                if old_nesab_acheived and not nesab_acheived:
                                    for i in list_zakahdetails_all_1:
                                        if i.active:
                                            i.start_day=date(1111,1,1)
                                            i.deserve_day=date(1111,1,1)
                                            i.save()
                                elif not old_nesab_acheived and nesab_acheived:
                                    for i in list_zakahdetails_all_1:
                                        if i.active:
                                            i.start_day=list_zakahdetails_all_1[new_item_index_all].saving_day
                                            i.deserve_day=list_zakahdetails_all_1[new_item_index_all].saving_day+timedelta(days=354)
                                            i.save()

                    if list_zakahdetails_all_1[new_item_index_all].active==False:
                        list_zakahdetails_all_1[new_item_index_all].start_day=date(1111,1,1)
                        list_zakahdetails_all_1[new_item_index_all].deserve_day=date(1111,1,1)
                    list_zakahdetails_all_1[new_item_index_all].save()
                    print len(list_zakahdetails_all_1),87876565
                    updatesummary_o.total_saving=list_zakahdetails_all_1[-1].saving
                    updatesummary_o.save()
                request.session['mes_main'] = 'تم تحديث بياناتك بنجاح'
            else:
                monthly_form = monthlysave_form()
                request.session['mes_main'] = 'برجاء ادخال جميع البيانات بصورة صحيحة'
        return HttpResponseRedirect(reverse('main'))
    request.session['mes_main'] ='برجاء تسجيل الدخول اولا ثم تحديث بيانات مدخراتك'#sending message to main_f function
    return HttpResponseRedirect(reverse('main'))

########################################################################

########################################################################

def signout_f(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))