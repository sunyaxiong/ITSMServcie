from rest_framework import viewsets
from django.contrib.auth.models import User

from .models import Profile, Channel
from .serializers import ProfileSerializer, ChannelSerializer, UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):

    model = Profile
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = Profile.objects.filter()
        # if self.kwargs.get('city'):
        #     queryset = queryset.filter(city=self.kwargs['city'])
        return queryset


class ChannelViewSet(viewsets.ModelViewSet):

    model = Channel
    serializer_class = ChannelSerializer

    def get_queryset(self):
        queryset = Channel.objects.filter()
        return queryset


class UserViewSet(viewsets.ModelViewSet):

    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter()
        return queryset
