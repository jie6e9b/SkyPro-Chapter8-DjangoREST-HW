from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from .models import User
from lms.models import Payment
from .serializers import UserSerializer

# Create your views here.


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

