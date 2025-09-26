from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

import lms.models
from lms.models import Course, Lesson

# Create your models here.


class User(AbstractUser):
    # username остаётся как в AbstractUser
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"  # вход по email
    REQUIRED_FIELDS = ["username"]  # username обязателен при createsuperuser

    def __str__(self):
        return f"{self.username} ({self.email})"


class Payment(models.Model):
    """Модель платежей:
    - пользователь
    - дата оплаты
    - оплаченный курс или урок
    - сумма
    - способ оплаты (наличные или перевод)"""

    CASH = "cash"
    CARD = "card"
    PAYMENT_METHODS = [
        (CASH, "Наличные"),
        (CARD, "Перевод на счет"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_payments",
        null=True,
        blank=True,
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="lesson_payments",
        null=True,
        blank=True,
        verbose_name="Урок",
    )
    payment_type = models.CharField(
        max_length=100, choices=PAYMENT_METHODS, verbose_name="Способ оплаты"
    )
    payment_price = models.DecimalField(
        max_digits=100, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"{self.user} - {self.payment_price} ({self.payment_type})"
