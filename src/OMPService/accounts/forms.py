#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    # password2 = forms.CharField(label='确认密码',widget=forms.PasswordInput())
    # email = forms.EmailField(label='电子邮件')


class RegisterForm(forms.Form):

    username = forms.CharField(label="用户名", max_length=128)
    email = forms.EmailField(label="邮箱")
    org = forms.CharField(label="组织", max_length=128)
    position = forms.CharField(label="岗位角色", max_length=128)
    password = forms.CharField(label="用户名", max_length=128)
    password2 = forms.CharField(label="用户名", max_length=128)


class ProfileForm(forms.Form):

    email = forms.EmailField(label="邮箱")
    # org = forms.CharField(label="组织", max_length=128)
    phone = forms.CharField(label="电话", max_length=128)

    def clean_phone(self):
        if self.data.get("phone") == "None":
            # raise ValidationError("请指派处理人")
            [].sort()