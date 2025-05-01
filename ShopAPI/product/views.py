from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters

from .filters import ProductItemFilter
from .serializers import *
from .models import *

# Create your views here.

# All Products by Category
class ProductByCategory(APIView):
    def get(self, request, slug):
        category = Category.objects.get(slug=slug)

        breadcrumbs = CategorySerializer(category).data

        products = Product.objects.select_related('category_id')\
                    .filter(category_id__slug=slug)
        products_data = ProductSerializer(products, many=True).data

        header = HeaderFooterSerializer(Product.objects.all()).data

        return Response({
            'breadcrumbs': breadcrumbs,
            'children': products_data,
            'header&footer': header
        })

class ItemsByProducts(generics.ListAPIView):
    pass

# all products are given, people can seaarch and filter
class SearchAndFilterProductItems(generics.ListAPIView):
    serializer_class = ProductItemSerializer
    filterset_class = ProductItemFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'color']
    def get_queryset(self):
        return ProductItem.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        filter = AttributeType.objects.all()
        filter_data = FilterSerializer(filter, many=True).data

        header = HeaderFooterSerializer(Product.objects.all()).data

        return Response({
            'filter': filter_data,
            'products': serializer.data,
            'header&footer': header
        })

# Retrieve a Product Item Cart Separately with an ability to switch colors and memory
class RetrieveProductItem(generics.RetrieveAPIView):

    serializer_class = FullProductItemSerializer

    def get_object(self):
        return ProductItem.objects.get(slug=self.kwargs['item_slug'])

    def retrieve(self, request, *args, **kwargs):
        query_set = self.get_object()
        product = self.get_serializer(query_set).data

        parent = self.kwargs['product_slug']
        family = Product.objects.get(slug=parent).items.all()
        family_data = ShortProductItemSerializer(family, many=True).data

        return Response({
            'product': product,
            'family': family_data
        })