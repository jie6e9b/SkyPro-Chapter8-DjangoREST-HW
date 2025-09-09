from django.shortcuts import render
from rest_framework import viewsets, generics
# Create your views here.

from rest_framework import generics
from .models import User
from .serializers import UserSerializer


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
