# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    # updated only when the creation takes place
    created_on = models.DateTimeField(auto_now_add=True)

    # updated every time there's a change
    updated_on = models.DateTimeField(auto_now=True)
    has_verified = models.BooleanField(default=False)


class SessionToken(models.Model):
    user = models.ForeignKey(User)
    session_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = uuid.uuid4()


class Post(models.Model):
    user = models.ForeignKey(User)
    # this is the folder name to which the image will be uploaded and saved
    image = models.FileField(upload_to='user_image_set')
    image_url = models.CharField(max_length=255)
    captions = models.CharField(max_length=240)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
