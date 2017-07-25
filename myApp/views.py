# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import datetime
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password, check_password
from models import User, SessionToken, Post, Like, Comment
from instaClone.settings import BASE_DIR
from imgurpython import ImgurClient
# Create your views here.


CLIENT_ID = '9b30aed478cd2af'

CLIENT_SECRET = 'f453269f0a01ef73760d0343ea5b4d9294ec06de'


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

    if user:
        posts = Post.objects.all().order_by('-created_on')
        #if Like.objects.filter(user=user, post_id=post_id).exists()
        for post in posts:
            existing_like = Like.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.creator_has_liked = True
                print 'has liked!'
        #num_of_likes =
        return render(request, 'login_success.html', {'posts': posts, 'msg':'Welcome '+user.username})
    else:
        return redirect('/login/')
    #return render(request,'login_success.html',response_data)


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
                client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
                path = str(BASE_DIR +'\\user_image_set\\'+ post.image.url)
                print post.image_url
                post.image_url = client.upload_from_path(path, anon=True)['link']

                post.save()
            return render(request,'login_success.html')
    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id

            existing_like = Like.objects.filter(post_id=post_id, user=user).first()

            if not existing_like:
                print 'liking post'
                Like.objects.create(post_id=post_id, user=user)
            else:
                print ' unliking post'
                existing_like.delete()

            return redirect('/login_success/')

    else:
        return redirect('/login/')



def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = Comment.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/login_success/')
        else:
            return redirect('/login_success/')
    else:
        return redirect('/login')



def check_validation(request):
  if request.COOKIES.get('session_token'):
    sess = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
    if sess:
      return sess.user
  else:
    return None