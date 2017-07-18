# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import datetime
from forms import SignUpForm
# Create your views here.


def signup_view(request):
    request.method == "GET"

    today = datetime.date.today()
    sign_up_form = SignUpForm()
    return render(request,'index.html',{'today':today, 'signup_form' :sign_up_form})

