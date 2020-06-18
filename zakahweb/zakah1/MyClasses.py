from django.contrib.auth.models import User
import datetime, operator, time
from datetime import date,timedelta

class auxilary():
    def chknon(a=1,b=1,c=1,d=1,e=1,f=1,g=1,h=1,i=1,j=1,k=1,l=1,m=1,n=1,o=1,p=1,q=1,r=1):
        if a==None or b==None or c==None or d==None or e==None or f==None:
            return False
        return True

#deduct_till_zero
# A function that accepts the 'deduction value' and a set of objects with values and dates
# it arranges objects descending by date; deduct the deduction value from arranged objects one by one until deduction
# reaches zero
    def deduct_till_zero(self,deduction_value,object_list):
        print 1111111111
        active_indication = deduction_value#a negative value
        object_list = sorted(object_list, key=operator.attrgetter('saving_day'), reverse=True)
        # to arrange a queryset
        for i in object_list:
            print 222222222222222222
            active_indication = active_indication + i.active_saving
            if active_indication <= 0:
                print 33333333333333
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
    def update_objects(self,previous_status,current_status,object2,object1,list_object1):
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

##a method that calculates the net deduct caused by all dates after certain date to previous dates
    def calc_net_deduc(self,obj_list):
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
    def list_deducted(self,obj_list,net_deduct):#net_deduct is a negative value
        withdrawl=0
        deducted_list=[]
        obj_list.reverse()
        for i in obj_list:
            if net_deduct>=0:
                break
            if i.net_save_increase<0:
                withdrawl+=i.net_save_increase
            elif withdrawl<0:
                withdrawl+=i.net_save_increase
                if withdrawl>0:#withdrawl equals the remaining in the net_save_increase after deducting the previous withdrawl
                                #now ready to deduct the net_deduct from the remaining-if it is >net_deduct
                    if abs(net_deduct)<=withdrawl:
                        j=[i,abs(net_deduct)]
                        deducted_list += [j]
                        break
                    else:
                        net_deduct+= withdrawl
                        j=[i,withdrawl]
                    deducted_list+= [j]
            else:
                print 'net_deduct',net_deduct
                net_deduct+=i.net_save_increase
                if net_deduct<0:
                    j=[i,i.net_save_increase]
                else:
                    j=[i,i.net_save_increase-net_deduct]
                deducted_list += [j]
        return deducted_list#a list of lists, each sub list contains the object and the deduction(positive value)
    def list_copy(self,list):
        new_list=[]
        for i in list:
            new_list.append(i)
        return new_list
