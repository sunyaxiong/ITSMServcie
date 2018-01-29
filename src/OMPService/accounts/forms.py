#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    # password2 = forms.CharField(label='确认密码',widget=forms.PasswordInput())
    # email = forms.EmailField(label='电子邮件')