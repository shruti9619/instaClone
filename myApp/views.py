# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
import datetime
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password, check_password
from models import User, SessionToken, Post, Like, Comment
from instaClone.settings import BASE_DIR
from imgurpython import ImgurClient
from clarifai.rest import ClarifaiApp , Image as ClImage
import requests
# Create your views here.


CLIENT_ID = '9b30aed478cd2af'

CLIENT_SECRET = 'f453269f0a01ef73760d0343ea5b4d9294ec06de'

PARALLEL_DOTS_KEY = "ddqUK3gJCSCzveJUZprtLXjHsiERfEa6dz0df1ZGi9c"



# password stored using hashing
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

            # to check if user with the same username or email already exists
            users = User.objects.all()
            # if Like.objects.filter(user=user, post_id=post_id).exists()
            for post in users:
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    print 'User exists!'
                    response_data['msg'] = 'Username already exists! Try adding numbers'
                    return render(request, 'index.html', response_data)

            #storing to the db
            user = User(name = name, username=username, password = make_password(password), email = email)
            user.save()
            return render(request,'signup_success.html', {'name':name})

    if request.method == "GET":
        today = datetime.date.today()
        sign_up_form = SignUpForm()
    return render(request, 'index.html', {'signup_form': sign_up_form})




# method to show login form
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
    # print 'login view exit'
    return render(request,'login.html',response_data)



# method visible after login is successful and feeds come here
def login_success_view(request):
    # print 'loginsuccessenter'
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



# provides view for the page to add posts
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

                if checkComment(caption) == 1:
                    post = Post(user=user, image=image, captions=caption)


                    path = str(BASE_DIR + '\\user_image_set\\' + post.image.url)
                    print post.image_url
                # adding imgur client to maintain url of images
                # try catch edge case if connection fails or image can't be uploaded
                    try:
                        client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
                        post.image_url = client.upload_from_path(path, anon=True)['link']
                    except:
                        return render(request, 'post.html', {'msg': 'Failed to upload! Try again later'})

                    post.save()
                    return render(request,'login_success.html',{'msg': 'Post added successfully!'})
                else:
                    return render(request, 'login_success.html', {'msg': 'Please avoid use of abusive language'})
    else:
        return redirect('/login/')



# provides method for like functionality
def like_view(request):
    liked_msg = ''
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id

            existing_like = Like.objects.filter(post_id=post_id, user=user).first()

            if not existing_like:
                # print 'liking post'
                Like.objects.create(post_id=post_id, user=user)
                liked_msg = 'Liked!'
            else:
                # print ' unliking post'
                existing_like.delete()
                liked_msg = 'Unliked!'

            return redirect('/login_success/',{'liked_msg': liked_msg})

    else:
        return redirect('/login/')



# method to provide form to add a comment
def comment_view(request):
    user = check_validation(request)
    abuse_msg = "nothing"
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')

            print checkComment(comment_text)
            if checkComment(comment_text) == 1:
                comment = Comment.objects.create(user=user, post_id=post_id, comment_text=comment_text)
                comment.save()
            else:
                abuse_msg = "Please avoid use of abusive language."
            return redirect('/login_success/', {'abuse_msg': abuse_msg})
        else:

            return redirect('/login_success/')
    else:
        return redirect('/login')



# method to return current user instance if valid and return none is invalid user
def check_validation(request):
  if request.COOKIES.get('session_token'):
    sess = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
    if sess:
      return sess.user
  else:
    return None



# method to check if img is valid for children
def checkImage():
    app = ClarifaiApp(api_key='ab7ff2b9dc2a4651909930166045d371')

    # get the general model
    model = app.models.get('general-v1.3')
    image = ClImage(file_obj=open('/home/user/image.jpeg', 'rb'))
    model.predict([image])
    # xd = model.predict_by_url(
    #     url=image_url)



# method to check if comment is decent or abusive with parallel dots
def checkComment(commenttext):
    req_json = None
    req_url = "https://apis.paralleldots.com/abuse"
    payload = {
  "text": commenttext,
  "apikey": PARALLEL_DOTS_KEY
}
    # 1 is for non abusive and 0 is for abusive
    try:
        req_json = requests.post(req_url, payload).json()
        if req_json is not None:
            # sentiment = req_json['sentiment']
            print req_json['sentence_type']
            print req_json['confidence_score']
            if req_json['sentence_type'] == "Non Abusive":
                if req_json['confidence_score'] > 0.60:
                    return 1
                else:
                    return 0
            else:
                return 0
    except:
        return 0





# method to log user out of his account
def logout_view(request):

    user = check_validation(request)

    if user is not None:
        latest_sessn = SessionToken.objects.filter(user=user).last()
        if latest_sessn:
            latest_sessn.delete()
            return redirect("/login/")
            # how to get cookies in python to delete cookie n session


# method to create upvote for comments
def upvote_view(request):
    if request.method == "POST":
        # increment upvote num
        print 'x'
