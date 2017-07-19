# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import datetime
from forms import SignUpForm, LoginForm
from django.contrib.auth.hashers import make_password, check_password
from models import User
# Create your views here.


def signup_view(request):

    if request.method == "POST":
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            name = sign_up_form.cleaned_data['name']
            email = sign_up_form.cleaned_data['email']
            password = sign_up_form.cleaned_data['password']

            #storing to the db
            user = User(name = name, password = make_password(password), email = email)
            user.save()
            return render(request,'signup_success.html',{'name':name})

    if request.method == "GET":
        today = datetime.date.today()
        sign_up_form = SignUpForm()
    return render(request, 'index.html', {'today': today, 'signup_form': sign_up_form})


def login_view(request):

    print 'utter shit'
    response_data = {}
    if request.method == "POST":

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('name')
            pwd = form.cleaned_data.get('password')
            user = User.objects.filter(name=username).first()

            if user:
                if check_password(pwd,user.password):
                    print 'User is logged in'
                    return render(request,'login_success.html')
                else:
                    print 'Incorrect Password! Please try again!'
                    print 'critical shit'


    elif request.method == "GET":
        print 'SHit'
        form = LoginForm()
    return render(request,'login.html',{'LoginForm': form})



def login_success_view(request):
    return render(request,'login_success.html')
