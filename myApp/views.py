# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import datetime
from forms import SignUpForm, LoginForm
from django.contrib.auth.hashers import make_password, check_password
from models import User, SessionToken
# Create your views here.


def signup_view(request):

    if request.method == "POST":
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            name = sign_up_form.cleaned_data['name']
            username = sign_up_form.cleaned_data['username'];
            email = sign_up_form.cleaned_data['email']
            password = sign_up_form.cleaned_data['password']

            #storing to the db
            user = User(name = name, username=username, password = make_password(password), email = email)
            user.save()
            return render(request,'signup_success.html',{'name':name})

    if request.method == "GET":
        today = datetime.date.today()
        sign_up_form = SignUpForm()
    return render(request, 'index.html', {'signup_form': sign_up_form})


def login_view(request):

    response_data = {}
    if request.method == "POST":

        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password')
            user = User.objects.filter(username=username).first()

            if user:
                if check_password(pwd, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    print 'User is logged in'
                    response = redirect('login_success/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                    #return render(request,'login_success.html')
                else:
                    response_data['msg'] = "Incorrect Password! Please try again!"
            else:
                response_data['msg'] = "Incorrect Username! Please try again!"



    response_data['form'] = LoginForm()
    return render(request,'login.html',response_data)



def login_success_view(request):
    response_data = {}
    user = check_validation(request)
    if user is not None:
        response_data['msg'] = "Welcome " + user.name
    else:
        response_data['msg'] = 'Cannot fetch the session details'
    return render(request,'login_success.html',response_data)


def check_validation(request):
  if request.COOKIES.get('session_token'):
    sess = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
    if sess:
      return sess.user
  else:
    return None