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

class ProductItemsByCategory(APIView):
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

# here filters might be implemented
# class SearchProducts(APIView):
#     def get(self, request, slug):
#         category = Category.objects.get(slug=slug)

#         breadcrumbs = CategorySerializer(category).data

#         products = ProductItem.objects.select_related('product_id__category_id').\
#             filter(product_id__category_id__slug=slug)

#         products_data = ProductItemSerializer(products, many=True).data

#         filter = AttributeType.objects.all()
#         filter_data = FilterSerializer(filter, many=True).data

#         return Response(
#             {
#                 'breadcrumbs': breadcrumbs,
#                 'products': products_data,
#                 'filter': filter_data
#             })

class AllProductsItemsByCategory(generics.ListAPIView):
    serializer_class = ProductItemSerializer
    filterset_class = ProductItemFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'color']
    def get_queryset(self):
        # slug = self.kwargs['slug']
        return ProductItem.objects.all()
        #select_related('product_id__category_id').\
            #filter(product_id__category_id__slug=slug)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # slug = self.kwargs['slug']
        # category = Category.objects.get(slug=slug)
        # breadcrumbs = CategorySerializer(category).data

        filter = AttributeType.objects.all()
        filter_data = FilterSerializer(filter, many=True).data

        return Response({
            # 'breadcrumbs': breadcrumbs,
            'filter': filter_data,
            'products': serializer.data,
        })
