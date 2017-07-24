from models import User, Post
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