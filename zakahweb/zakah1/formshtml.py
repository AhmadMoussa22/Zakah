# coding=<utf-8>
#!/usr/bin/python
#  -*- coding: utf-8 -*-
# A file we create just to organize our work i.e. to create classes each class (an object of it) represents a form
#  to be used in the html file.... same as "shared file concept; the html form(which takes its items from it)
#  writes in it"
from django import forms
import datetime
from datetime import date
class signin_form(forms.Form):
    user_name=forms.CharField(max_length=55)
    pass_word=forms.CharField(widget=forms.PasswordInput(),max_length=20)

class monthlysave_form(forms.Form):
    month_save_date=forms.CharField(max_length=100)
    month_save_le=forms.IntegerField()
class signup_form(forms.Form):
    init_save_date=forms.DateField()
    init_save_le=forms.IntegerField()
class initzakah_form(forms.Form):
    pass