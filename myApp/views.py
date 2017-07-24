# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import datetime
from forms import SignUpForm, LoginForm, PostForm
from django.contrib.auth.hashers import make_password, check_password
from models import User, SessionToken, Post
# Create your views here.


def signup_view(request):
    response_data = {}
    if request.method == "POST":
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            name = sign_up_form.cleaned_data['name']
            username = sign_up_form.cleaned_data['username'];
            email = sign_up_form.cleaned_data['email']
            password = sign_up_form.cleaned_data['password']

            if len(username) < 4:
                response_data['msg']= 'Username should have atleast 4 characters'
            if len(password) < 5:
                response_data['msg'] = 'Password should have atleast 5 characters'

            #storing to the db
            user = User(name = name, username=username, password = make_password(password), email = email)
            user.save()
            return render(request,'signup_success.html', {'name':name})

    if request.method == "GET":
        today = datetime.date.today()
        sign_up_form = SignUpForm()
    return render(request, 'index.html', {'signup_form': sign_up_form})


def login_view(request):

    response_data = {}
    if request.method == "POST":
        print 'post in login'
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
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
    print 'loginviewexit'
    return render(request,'login.html',response_data)



def login_success_view(request):
    print 'loginsuccessenter'
    response_data = {}
    user = check_validation(request)
    if user is not None:
        response_data['msg'] = "Welcome " + user.name
    else:
        response_data['msg'] = 'Cannot fetch the session details'
    return render(request,'login_success.html',response_data)


def post_view(request):

    user = check_validation(request)

    if user:
        if request.method == 'GET':
            form = PostForm()
            return render(request, 'post.html', {'form': form})
        elif request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data['image']
                caption = form.cleaned_data['captions']

                post = Post(user=user, image=image, captions=caption)
                post.save()
        return render(request,'login.html')
    else:
        return redirect('/login/')





def check_validation(request):
  if request.COOKIES.get('session_token'):
    sess = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
    if sess:
      return sess.user
  else:
    return None