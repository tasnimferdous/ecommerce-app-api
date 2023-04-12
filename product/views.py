"""
Views for the product APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product
from product import serializers

class ProductViewSet(viewsets.ModelViewSet):
    """View for managing product list"""
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user = self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer_class as per request"""
        if self.action == 'list':
            return serializers.ProductSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Product"""
        serializer.save(user = self.request.user)