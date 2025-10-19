import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'lms.tests.test_settings'

from unittest.mock import patch, MagicMock
from django.test import TestCase
from lms.stripe_services import StripeService


class StripeServiceTests(TestCase):
    @patch('stripe.Product.create')
    def test_create_product(self, mock_create_product):
        """Тест создания продукта в Stripe"""
        mock_create_product.return_value = MagicMock(id='prod_test123')

        service = StripeService()
        product = service.create_product('Test Product', 'Test Description')

        self.assertEqual(product.id, 'prod_test123')
        mock_create_product.assert_called_once_with(
            name='Test Product',
            description='Test Description'
        )
