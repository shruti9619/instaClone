from models import User
from django import forms


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['name','email', 'password']


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'password']