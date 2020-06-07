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
    def deduct_till_zero(self,deduction_value,object_set):
        active_indication = deduction_value#a negative value
        object_set = sorted(object_set, key=operator.attrgetter('saving_day'), reverse=True)
        # to arrange a queryset
        for i in object_set:
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
        return

#update_objects
#case1: previous:flase & current:false-->change nothing
#case2: previous:flase & current:True-->update stare_day and deserve day in the set of object1(all the detailed table)
#     and update nesab_day in object 2(summary table)
#case3: previous:true & current:true(and deposit not withdrawl)-->update start_day and nesab_day of object1(current entry only)
#case4: previous:true & current:false-->update stare_day and deserve day in the set of object1(all the detailed table)
#     and update nesab_day in object 2(summary table)[to equale inactive date]
    def update_objects(self,previous_status,current_status,object2,object1,set_object1):
        if previous_status == False:
            if current_status:  # previous_status False and current_status True
                object2.nesab_day = object1.saving_day
                object2.save()
                object1.start_day=object1.saving_day
                object1.deserve_day=object1.start_day + timedelta(days=354)
                object1.save()
                for i in set_object1:
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
                for i in set_object1:
                    i.start_day = date(1111, 1, 1)
                    i.deserve_day = date(1111, 1, 1)
                    i.save()
        return object2,object1,set_object1