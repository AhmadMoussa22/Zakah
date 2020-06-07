# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class zakah_register_c(models.Model): #zakah register table
    username=models.ForeignKey(User,on_delete=models.CASCADE)#This means that this colmn of the table 'zreg_c'
    # is an object of the table 'User'
    saving=models.IntegerField() #in case deposite, to be inserted by minus
    zakah=models.FloatField() # the amount of the required zakah
    saving_day=models.DateField() # date of the money earned
    start_day=models.DateField(default=date(1111,1,1)) # starting date to calculate 7awl
    deserve_day=models.DateField(default=date(1111,1,1)) # Due date to pay zakah
    active_saving=models.FloatField(default=0)
    active=models.BooleanField(default=True)
    nesab_acheived=models.BooleanField(default=True)

class zakah_summary_c(models.Model): #zakah register table
    username=models.ForeignKey(User,on_delete=models.CASCADE)#This means that this colmn of the table 'zreg_c'
    # is an object of the table 'User'
    total_saving=models.FloatField(default=0)
    nesab_day=models.DateField(default=date(1111,1,1)) # the date of reaching nesab
    required_zakah=models.FloatField(default=0)
