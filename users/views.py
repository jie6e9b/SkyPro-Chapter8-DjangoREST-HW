from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer

# Create your views here.


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)


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

    queryset = Payment.objects.select_related("user", "course", "lesson").all()
    serializer_class = PaymentSerializer

    # Фильтры и поиск
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["course", "lesson", "payment_type", "user"]  # фильтры
    ordering_fields = ["payment_date"]  # сортировка
    search_fields = [
        "user__username",
        "user__email",
    ]  # поиск по имени и email пользователя
