#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import ValidationError

from .models import Event, EventProcessLog
from .models import Change
from .models import Issue
from .models import SatisfactionLog


class EventDetailForm(forms.Form):

    emergency_degree = forms.ChoiceField(required=False)
    solution = forms.CharField(required=False)
    technician = forms.CharField(required=False)
    attach_file = forms.FileField(required=False)

    def clean_technician(self):
        if self.data.get("technician") == "None":
            raise ValidationError("请指派处理人")


class ChangeDetailForm(forms.Form):

    emergency_degree = forms.CharField(required=False)
    solution = forms.CharField(required=False)
    node_handler = forms.CharField()
    attach_file = forms.FileField(required=False)
    description = forms.CharField(required=False)


class ChangeDetailModelForm(forms.ModelForm):

    description = forms.Textarea(attrs={"class": "type"})

    class Meta:
        model = Change
        fields = "__all__"


class EventDetailModelForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-group"}), label="事件名称"
    )
    description = forms.CharField(
        widget=forms.Select(attrs={"class": "form-control"}), label="事件描述"
    )

    class Meta:
        model = Event
        fields = "__all__"


class IssueDetailForm(forms.Form):

    emergency_degree = forms.ChoiceField(choices=Change.EMERGENCY_DEGREE)
    solution = forms.CharField(required=False)
    handler = forms.CharField()
    attach_file = forms.FileField(required=False)
    description = forms.CharField(required=False)

    def clean_handler(self):
        if self.data.get("handler") == "None":
            raise ValidationError("请指派处理人")


class SatisfactionForm(forms.Form):

    # event = forms.CharField(required=False)
    sati_id = forms.IntegerField(required=True)
    comment = forms.CharField(required=True)
    content = forms.CharField(required=False)
    is_ended = forms.CharField(required=False)


class IssueToKnowForm(forms.Form):

    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
    attach_file = forms.FileField()
    issue_id = forms.IntegerField(required=False)
    issue_name = forms.CharField(required=False)
    classify = forms.CharField(required=False)

