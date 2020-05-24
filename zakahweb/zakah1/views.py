# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .MyClasses import auxilary

# Create your views here.
def main_f(request):
    return render (request,'main_t.html',{})
def signup_f(request):
    mess=''
    my_auxilary = auxilary()
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        firstname=request.POST['fname']
        lastname=request.POST['lname']
        print email
        try:  # to check for username duplication error
            print email
            newuser =User.objects.create_user(username, email, password)
            newuser.first_name=firstname
            newuser.last_name=lastname
            newuser.save()
            return HttpResponseRedirect('/zakah1/signup/')#To initialize the form data,,
            # to overcome the problem of form resubmission when refresh
        except:
            mess='Duplicated Data'
    return render(request, 'sign up.html', {'d':mess})