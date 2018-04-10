from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


from .models import Profile
from .models import Channel


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"

    # def validate_username(self, value):
    #     try:
    #         user = User.objects.get(username=value)
    #     except Exception as e:
    #         raise ValidationError(e)


class ChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
