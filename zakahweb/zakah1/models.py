# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class zreg_c(models.Model): #zakah register table
    username=models.ForeignKey(User,on_delete=models.CASCADE)#This means that this colmn of the table 'zreg_c'
    # is an object of the table 'User'
    savingday=models.DateField()
    startday=models.DateField()
    deserveday=models.DateField()

