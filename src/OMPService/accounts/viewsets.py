from rest_framework import viewsets

from .models import Profile, Channel
from .serializers import ProfileSerializer, ChannelSerializer


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

