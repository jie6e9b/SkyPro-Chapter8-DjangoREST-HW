from django.shortcuts import render
from rest_framework import viewsets, generics
# Create your views here.

from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD для платежей.
    Поддержка фильтрации и сортировки:
    - по курсу
    - по уроку
    - по способу оплаты
    - по пользователю
    Поддержка поиска по имени пользователя
    """
    queryset = Payment.objects.select_related('user', 'course', 'lesson').all()
    serializer_class = PaymentSerializer

    # Фильтры и поиск
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['course', 'lesson', 'payment_type', 'user']  # фильтры
    ordering_fields = ['payment_date']  # сортировка
    search_fields = ['user__username', 'user__email']  # поиск по имени и email пользователя