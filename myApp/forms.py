from models import User, Post, Like, Comment
from django import forms


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['name','username','email', 'password']


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'captions']


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ['post']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text', 'post', 'id']

from django import forms

class UpvoteForm(forms.Form):
    id = forms.IntegerField()

class SearchForm(forms.Form):
    searchquery = forms.CharField();
