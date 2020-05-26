#!/usr/bin/python
#  -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .MyClasses import auxilary
from .forms import signin_form

# Create your views here.
# cd c:\work\python work\zakah\zakah\zakahweb
# python manage.py runserver
def main_f(request):
    return render (request,'main_t.html',{})

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
            login(request,newuser)
            return HttpResponseRedirect('/zakah1/profile/')
        except:
            mess='Duplicated Data'
    return render(request, 'sign up.html', {'d':mess,'f':f1})

#####################################################################

#####################################################################

def signin_f(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/zakah1/profile')
    if request.method == 'POST':
        user_name = request.POST['user_name']
        pass_word = request.POST['pass_word']
        res = authenticate(username=user_name, password=pass_word)
        if res is not None:
            login(request, res)
            return HttpResponseRedirect('/zakah1/profile/')
        else:
            mess='Eigther username or password is incorrect'
            return render(request,'sign in.html',{'mess':mess})
    return render(request,'sign in.html',{})

#######################################################################

#######################################################################

def profile_f(request):
    print request.user.is_authenticated()
    if request.user.is_authenticated():
        username=request.user.username
        return render(request,'profile.html',{'name': username})
    return HttpResponseRedirect('/zakah1/signin',{'name': 'Aloooooo'})

########################################################################

########################################################################

def signout_f(request):
    logout(request)
    return HttpResponse('Successfuly logged out')