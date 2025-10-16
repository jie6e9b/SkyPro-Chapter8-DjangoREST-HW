from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson, Payment

User = get_user_model()


class PaymentTests(APITestCase):
    """Тесты для проверки работы PaymentViewSet"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            price=1000.00,
            owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            course=self.course,
            price=100.00,
            owner=self.user
        )

    # ----------------------------
    # ТЕСТ СОЗДАНИЯ ПЛАТЕЖА ДЛЯ КУРСА
    # ----------------------------
    @patch('lms.stripe_services.StripeService.create_product')
    @patch('lms.stripe_services.StripeService.create_price')
    @patch('lms.stripe_services.StripeService.create_session')
    def test_create_payment_for_course(self, mock_create_session, mock_create_price, mock_create_product):
        """Тест создания платежа для курса"""
        mock_create_product.return_value = MagicMock(id='prod_test123')
        mock_create_price.return_value = MagicMock(id='price_test123')
        mock_create_session.return_value = ('sess_test123', 'https://stripe.com/test-payment')

        url = reverse('payment-create-payment')
        data = {'course': self.course.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_url', response.data)
        self.assertIn('id', response.data)

        payment = Payment.objects.get(id=response.data['id'])
        self.assertEqual(payment.course, self.course)
        self.assertEqual(payment.payment_status, 'pending')
        self.assertEqual(payment.payment_price, self.course.price)

    # ----------------------------
    # ТЕСТ СОЗДАНИЯ ПЛАТЕЖА ДЛЯ УРОКА
    # ----------------------------
    @patch('lms.stripe_services.StripeService.create_product')
    @patch('lms.stripe_services.StripeService.create_price')
    @patch('lms.stripe_services.StripeService.create_session')
    def test_create_payment_for_lesson(self, mock_create_session, mock_create_price, mock_create_product):
        """Тест создания платежа для урока"""
        mock_create_product.return_value = MagicMock(id='prod_test123')
        mock_create_price.return_value = MagicMock(id='price_test123')
        mock_create_session.return_value = ('sess_test123', 'https://stripe.com/test-payment')

        url = reverse('payment-create-payment')
        data = {'lesson': self.lesson.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('payment_url', response.data)

    # ----------------------------
    # ТЕСТ СОЗДАНИЯ ПЛАТЕЖА БЕЗ КУРСА/УРОКА
    # ----------------------------
    def test_create_payment_without_course_or_lesson(self):
        """Тест создания платежа без указания курса или урока"""
        url = reverse('payment-create-payment')
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # ----------------------------
    # ТЕСТ ПРОВЕРКИ СТАТУСА ПЛАТЕЖА
    # ----------------------------
    @patch('lms.stripe_services.StripeService.get_payment_status')
    def test_check_payment_status(self, mock_get_payment_status):
        """Тест проверки статуса платежа"""
        payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            payment_price=self.course.price,
            payment_status='pending',
            stripe_payment_id='sess_test123'
        )

        mock_get_payment_status.return_value = 'paid'

        url = reverse('payment-check-status', args=[payment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_status'], 'paid')

        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, 'paid')

    # ----------------------------
    # ТЕСТ НЕАВТОРИЗОВАННОГО ДОСТУПА
    # ----------------------------
    def test_check_payment_status_unauthorized(self):
        """Тест проверки статуса платежа неавторизованным пользователем"""
        self.client.logout()
        url = reverse('payment-check-status', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)