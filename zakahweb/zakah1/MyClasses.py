from django.contrib.auth.models import User
import datetime, operator, time, copy
from datetime import date,timedelta

class auxilary():
    def chknon(a=1,b=1,c=1,d=1,e=1,f=1,g=1,h=1,i=1,j=1,k=1,l=1,m=1,n=1,o=1,p=1,q=1,r=1):
        if a==None or b==None or c==None or d==None or e==None or f==None:
            return False
        return True

#a method that reads old list and the new item-->returns the new list and its length,
#the status of override, and duplicate, the position of the new item in the list and its index
    def update_list_c(self,list_zakahdetails_all,updatedetails_o):
        override=False
        duplicate=False
        for old in list_zakahdetails_all:
            if updatedetails_o.saving_day == old.saving_day:
                override = True
                if updatedetails_o.saving == old.saving:
                    duplicate = True
                    list_zakahdetails_all_1=[]
                    new_item_index_all=None
                    break
                else:
                    new_item_index_all = list_zakahdetails_all.index(old)
                    list_zakahdetails_all_1 = copy.deepcopy(list_zakahdetails_all)
                    list_zakahdetails_all_1[new_item_index_all].saving = updatedetails_o.saving
                    list_zakahdetails_all_1[new_item_index_all].nesab_acheived = updatedetails_o.nesab_acheived
                    # if override and no duplicate create the new list(with the new item added and keep the old list)
                break
        if not override:# if not override create the new list(with the new item added and keep the old list)
            list_zakahdetails_all_1 = copy.deepcopy(list_zakahdetails_all)
            list_zakahdetails_all_1.append(updatedetails_o)
            list_zakahdetails_all_1 = sorted(list_zakahdetails_all_1, key=operator.attrgetter('saving_day'))
            new_item_index_all = list_zakahdetails_all_1.index(updatedetails_o)
        length_list_all = len(list_zakahdetails_all_1)
        if new_item_index_all==0:
            new_item_position='first'
        elif new_item_index_all<length_list_all-1:
            new_item_position='middle'
        else:
            new_item_position='last'

        return duplicate,override,list_zakahdetails_all_1,length_list_all,new_item_index_all,new_item_position

    def set_item_inactive_c(self,list,item_index):
        list[item_index].active_saving = 0
        list[item_index].active = False
        list[item_index].zakah = 0
        list[item_index].start_day = date(1111, 1, 1)
        list[item_index].deserve_day = date(1111, 1, 1)
        return list
    #a method that reads the list and the index of the item --> returrns reset(true/false) and index of next active item

    def reset_nextactive_c(self,list,index):
        reset=False
        next_active_item_index=None
        index_list=range(index,len(list))
        for i in index_list:
            if i==index:
                continue
            if list[i].active:
                next_active_item_index=i
                if list[i].start_day!=list[i].saving_day:
                    reset=True
                    break
            elif not list[i].nesab_acheived and not reset:
                reset=True
        return reset,next_active_item_index

    #deduct_till_zero
# A function that accepts the 'deduction value' and a set of objects with values and dates
# it arranges objects descending by date; deduct the deduction value from arranged objects one by one until deduction
# reaches zero
    def deduct_till_zero_c(self,deduction_value,object_list):
        print 1111111111
        active_indication = deduction_value#a negative value
        object_list = sorted(object_list, key=operator.attrgetter('saving_day'), reverse=True)
        # to arrange a queryset
        for i in object_list:
            print 222222222222222222
            active_indication = active_indication + i.active_saving
            if active_indication <= 0:
                print 33333333333333
                #self.set_item_inactive_c(object_list,i)
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
        return  active_indication

#update_objects
#case1: previous:flase & current:false-->change nothing
#case2: previous:flase & current:True-->update stare_day and deserve day in the set of object1(all the detailed table)
#     and update nesab_day in object 2(summary table)
#case3: previous:true & current:true(and deposit not withdrawl)-->update start_day and nesab_day of object1(current entry only)
#case4: previous:true & current:false-->update stare_day and deserve day in the set of object1(all the detailed table)
#     and update nesab_day in object 2(summary table)[to equale inactive date]
    def update_objects_c(self,previous_status,current_status,object2,object1,list_object1):
        if previous_status == False:
            if current_status:  # previous_status False and current_status True
                object2.nesab_day = object1.saving_day
                object2.save()
                object1.start_day=object1.saving_day
                object1.deserve_day=object1.start_day + timedelta(days=354)
                object1.save()
                for i in list_object1:
                    i.start_day = object1.saving_day
                    i.deserve_day = i.start_day + timedelta(days=354)
                    i.save()
        else:  # previous_status = True
            if current_status:  # current_status
                if object1.active:  # deposite not withdrawll
                    object1.start_day = object1.saving_day
                    object1.deserve_day = object1.start_day + timedelta(days=354)
                    object1.save()
            else:  # previous_status True and current_status False
                object2.nesab_day = date(1111, 1, 1)
                object2.save()
                for i in list_object1:
                    i.start_day = date(1111, 1, 1)
                    i.deserve_day = date(1111, 1, 1)
                    i.save()
        return object2,object1,list_object1

    def readjust_active_saving_c(self,list,index,total_active_saving):
        if list[index].net_save_increase >= total_active_saving:
            print 'inside if if list_zakahdetails_all_1[0].net_save_increase >= total_active_saving_0'
            list[index].active_saving = total_active_saving
            list[index+1].active_saving = 0
        else:
            print 'inside else; i.e. if list_zakahdetails_all_1[0].net_save_increase < total_active_saving_0'
            list[index].active_saving = list[index].net_save_increase
            list[index+1].active_saving = total_active_saving - list[index].net_save_increase
        return list

    def undo_dates_reset_c(self,list,index):
        x = range(0,index)
        x.reverse()
        date_o = list[index].saving_day
        sw = False
        for i in x:  # update previous items(they were affected by old item)
            if list[i].nesab_acheived and not sw:
                if list[i].active:
                    date_o = list[i].saving_day
                    list[i].start_day = list[i].saving_day
                    list[i].deserve_day = list[i].saving_day + timedelta(
                        days=354)
                    list[i].save()
            else:
                sw = True
                if list[i].active:
                    list[i].start_day = date_o
                    list[i].deserve_day = date_o + timedelta(days=354)
                    list[i].save()
        return list

        ##a method that calculates the net deduct caused by all dates after certain date to previous dates
    def calc_net_deduc_c(self,obj_list):
        net_deduct=0
        for i in obj_list:
            print 'aa',obj_list.index(i),i.saving_day,i.net_save_increase,i.active_saving,net_deduct
            if i.active_saving != 0.0:
                break
            else:
                net_deduct=net_deduct+i.net_save_increase
            print net_deduct
        return net_deduct

##a method that reads a total deduct till specific date and returns a list of the objects affected by THIS deduct
    def list_deducted_c(self,obj_list,net_deduct):#net_deduct is a negative value
        withdrawl=0#old deductions
        deducted_list=[]
        obj_list.reverse()
        for i in obj_list:
            print 'befor','withdrawl=',withdrawl,'net_deduct=',net_deduct,'saving_date=',i.saving_day
            if net_deduct>=0:#upper deductions(-ve value) finished
                break
            if i.net_save_increase<0:
                print '1'
                withdrawl+=i.net_save_increase
            elif withdrawl<0:#periority to deduct old deductions-if exists- before upper deductions
                print '2'
                withdrawl+=i.net_save_increase#execute deduction as withdrawl is +ve and net save increase is -ve
                if withdrawl>0:#withdrawl equals the remaining in the net_save_increase after deducting the previous withdrawl
                    print '2-1'#now ready to deduct the net_deduct from the remaining-if it is >net_deduct
                    if abs(net_deduct)<=withdrawl:
                        print '2-1-1'
                        j=[i,abs(net_deduct)]
                        deducted_list += [j]
                        break
                    else:
                        print '2-1-2'
                        net_deduct+= withdrawl
                        j=[i,withdrawl]
                    deducted_list+= [j]
                    withdrawl=0#re-initialize withdrawl
            else:
                print '3'
                print 'net_deduct',net_deduct
                net_deduct+=i.net_save_increase
                if net_deduct<0:
                    print '3-1'
                    j=[i,i.net_save_increase]
                else:
                    print '3-2'
                    j=[i,i.net_save_increase-net_deduct]
                deducted_list += [j]
            print 'after', 'withdrawl=', withdrawl, 'net_deduct=', net_deduct, 'saving_date=', i.saving_day
        return deducted_list#a list of lists, each sub list contains the object and the deduction(positive value)
    def list_copy_c(self,list):
        new_list=[]
        for i in list:
            new_list.append(i)
        return new_list
    def return_deducted_c(self,list_all,deduction_list):
        for i in deduction_list:
            print'inside return deducted loop_1'
            index = list_all.index(i[0])
            print 'brfore',list_all[index].saving_day,list_all[index].active_saving
            list_all[index].active_saving += i[1]
            if list_all[index].active_saving > 0:
                list_all[index].active = True
            else:#to be deleted; new active saving always +ve
                list_all[index].active = False
                list_all(index).start_day=date(1111,1,1)
                list_all(index).deserve_day=date(1111,1,1)

            list_all[index].zakah = .025 * list_all[index].active_saving
            list_all[index].save()
        return list_all