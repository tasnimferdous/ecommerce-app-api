"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

class ModelTests(TestCase):
    """ Test model. """
    def test_create_user_with_email_successful(self):
        """ Test for creating a user with an email is successfull. """
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test for a user without an email to raise valueError"""
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """Test for creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_product(self):
        """Test for creating a product successfully"""
        user = get_user_model().objects.create_user(
            email = 'test@example.com',
            password = 'testpass123',
        )
        product = models.Product.objects.create(
            user = user,
            product_title = 'Sample product',
            product_price = Decimal('10.5'),
            product_color = 'Maroon',
            product_details = 'Sample product description',
        )

        self.assertEqual(str(product), product.product_title)