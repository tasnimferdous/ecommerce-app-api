"""
Tests for product api
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product

from product.serializers import (
    ProductSerializer,
    ProductDetailSerializer,
)

PRODUCTS_URL = reverse('product:product-list')

def detail_url(product_id):
    """Create & return a product detail URL"""
    return reverse('product:product-detail', args = [product_id])

def create_product(user, **params):
    """Create and return a sample product"""
    product = {
        'product_title' : 'Sample product',
        'product_price' : Decimal('10.5'),
        'product_color' : 'Maroon',
        'product_details' : 'Sample product description',
    }
    product.update(params)
    product = Product.objects.create(user = user, **product)

    return product

def create_user(**params):
    """Create & return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicProductAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = 'test@example.com', password = 'testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_product(self):
        """Test retrieving products list"""
        create_product(user = self.user)
        create_product(user = self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_product_list_limited_to_user(self):
        """Test list of products is limited to authenticated user."""
        other_user = create_user(email = 'other@example.com', password = 'testpass123')
        create_product(user=other_user)
        create_product(user=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_product_detail(self):
        """Test to get details of a poduct"""
        product = create_product(user = self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """Test for creating a product"""
        payload = {
        'product_title' : 'Sample product',
        'product_price' : Decimal('10.5'),
        'product_color' : 'Maroon',
        'product_details' : 'Sample product description',
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id = res.data['id'])

        for key, val in payload.items():
            self.assertEqual(getattr(product, key), val)
            # getattr(product, key) gets the value from product object mapping to the key
        self.assertEqual(product.user, self.user)

    def test_partial_update(self):
        """Test partial update of a product"""
        original_color = 'Maroon'
        product = create_product(
            user = self.user,
            product_title = 'Sample product',
            product_price = Decimal('10.5'),
            product_color = original_color,
        )
        payload = {'product_title':'New product'}
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.product_title, payload['product_title'])
        self.assertEqual(product.product_color, original_color)
        self.assertEqual(product.user, self.user)

    def test_full_update(self):
        """Test full update of a product"""
        product = create_product(
            user = self.user,
            product_title = 'Sample product',
            product_price = Decimal('10.5'),
            product_color = 'maroon',
        )
        payload = {
            'product_title': 'New product',
            'product_price': Decimal('10.5'),
            'product_color':'New color',
            'product_details':'New details',
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(product, key), val)
        self.assertEqual(product.user, self.user)

    def test_update_product_user_returns_error(self):
        """Test changing the product user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        product = create_product(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.user, self.user)

    def test_delete_product(self):
        """Test deleting a product successful."""
        product = create_product(user=self.user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_other_users_product_error(self):
        """Test trying to delete another users product gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        product = create_product(user=new_user)

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())