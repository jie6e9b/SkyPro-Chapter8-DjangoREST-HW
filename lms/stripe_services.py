import stripe
from django.conf import settings
from django.urls import reverse
from typing import Optional, Tuple

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_product(name: str, description: Optional[str] = None) -> stripe.Product:
        """Создание продукта в Stripe."""
        try:
            product = stripe.Product.create(
                name=name,
                description=description or name
            )
            return product
        except stripe.error.StripeError as e:
            raise ValueError(f"Ошибка при создании продукта в Stripe: {str(e)}")

    @staticmethod
    def create_price(product_id: str, price: int, currency: str = 'rub') -> stripe.Price:
        """Создание цены для продукта в Stripe."""
        try:
            price_object = stripe.Price.create(
                product=product_id,
                unit_amount=price * 100,
                currency=currency
            )
            return price_object
        except stripe.error.StripeError as e:
            raise ValueError(f"Ошибка при создании цены в Stripe: {str(e)}")

    @staticmethod
    def create_session(
            price_id: str,
            success_url: str,
            cancel_url: str,
            customer_email: Optional[str] = None
    ) -> Tuple[str, str]:
        """Создание платежной сессии в Stripe."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=customer_email
            )
            return session.id, session.url
        except stripe.error.StripeError as e:
            raise ValueError(f"Ошибка при создании сессии в Stripe: {str(e)}")

    @staticmethod
    def get_payment_status(session_id: str) -> str:
        """Проверка статуса платежа."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_status = session.payment_status
            if payment_status == 'paid':
                return 'paid'
            elif payment_status == 'unpaid':
                return 'pending'
            else:
                return 'failed'
        except stripe.error.StripeError as e:
            raise ValueError(f"Ошибка при получении статуса платежа: {str(e)}")

    @classmethod
    def create_payment_for_course(cls, course, user) -> Tuple[str, str]:
        """Создание платежа за курс."""
        # Создаем продукт, если его еще нет
        if not course.stripe_product_id:
            product = cls.create_product(
                name=course.name,
                description=f"Курс: {course.name}"
            )
            course.stripe_product_id = product.id
            course.save()

        # Создаем цену для продукта
        price = cls.create_price(
            product_id=course.stripe_product_id,
            price=int(course.price)  # Предполагается, что у курса есть поле price
        )

        # Создаем сессию оплаты
        success_url = settings.SITE_URL + reverse('payment_success')
        cancel_url = settings.SITE_URL + reverse('payment_cancel')

        session_id, session_url = cls.create_session(
            price_id=price.id,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user.email
        )

        return session_id, session_url
