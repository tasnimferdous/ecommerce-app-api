"""
Serializers for Product API
"""
from rest_framework import serializers

from core.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    class Meta:
        model = Product
        fields = ['id', 'product_title', 'product_price', 'product_color']
        read_onlyfields = ['id']

class ProductDetailSerializer(ProductSerializer):
    """Serializer for product detail"""

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['product_details', 'created', 'updated']