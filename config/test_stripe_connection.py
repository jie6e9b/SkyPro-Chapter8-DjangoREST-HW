import os
import django
from django.core.wsgi import get_wsgi_application

# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируйте Django
django.setup()

import stripe
from django.conf import settings

def test_stripe_connection():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Простой тестовый запрос к API
        stripe.Customer.list(limit=1)
        print("✅ Успешное подключение к Stripe API!")
        print(f"🔑 Используется API ключ: {stripe.api_key[:8]}...")
    except stripe.error.AuthenticationError:
        print("❌ Ошибка аутентификации. Проверьте ваш API ключ.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    test_stripe_connection()