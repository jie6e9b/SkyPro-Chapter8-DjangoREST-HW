from .models import CourseSubscription
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()



@shared_task
def send_course_update_notification(course_id, course_name, update_details):
    """
    Отправка уведомлений подписчикам об обновлении курса
    """
    # Получаем всех подписчиков курса
    subscriptions = CourseSubscription.objects.filter(course_id=course_id).select_related('user')

    subject = f'Обновление курса "{course_name}"'
    message = f'''
    Здравствуйте!

    Курс "{course_name}", на который вы подписаны, был обновлен.

    Изменения: {update_details}

    С уважением,
    Команда LMS
    '''

    # Отправляем письмо каждому подписчику
    for subscription in subscriptions:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.user.email],
            fail_silently=False,
        )

    return f"Уведомления отправлены {len(subscriptions)} подписчикам"

@shared_task
def deactivate_inactive_users():
    """
    Проверяет и деактивирует пользователей, которые не входили в систему более месяца
    """
    # Вычисляем дату, месяц назад от текущей
    month_ago = timezone.now() - timedelta(days=30)

    # Получаем всех активных пользователей, которые не входили более месяца
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=month_ago
    )

    deactivated_count = 0
    for user in inactive_users:
        # Деактивируем пользователя
        user.is_active = False
        user.save()

        # Отправляем уведомление пользователю
        send_mail(
            subject='Ваша учетная запись деактивирована',
            message='''
            Здравствуйте!

            Ваша учетная запись была деактивирована из-за отсутствия активности в течение последнего месяца.
            Для восстановления доступа, пожалуйста, свяжитесь с администратором.

            С уважением,
            Команда LMS
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        deactivated_count += 1

    return f"Деактивировано пользователей: {deactivated_count}"
