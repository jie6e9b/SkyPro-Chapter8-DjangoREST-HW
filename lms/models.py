from django.conf import settings
from django.db import models
from django.db.models import SET_NULL



class Course(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    preview = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=SET_NULL,
        null=True,
        verbose_name="Владелец",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
    )
    preview = models.ImageField(
        upload_to="lessons/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=SET_NULL,
        null=True,
        verbose_name="Владелец",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"{self.course.name} - {self.name}"


class CourseSubscription(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курсы"
        unique_together = ["user", "course"]  # Запрещаем дублирование подписок

    def __str__(self):
        return f"{self.user} - {self.course}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Курс")
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Урок")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    payment_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")

    # Stripe fields
    stripe_product_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="ID продукта в Stripe")
    stripe_price_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="ID цены в Stripe")
    stripe_payment_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="ID платежа в Stripe")
    stripe_payment_url = models.URLField(max_length=512, null=True, blank=True, verbose_name="URL для оплаты в Stripe")

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка оплаты'),
        ('canceled', 'Отменён'),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name="Статус платежа"
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ['-payment_date']

    def __str__(self):
        paid_for = self.course if self.course else self.lesson
        return f"Платёж {self.id} от {self.user} за {paid_for}"
