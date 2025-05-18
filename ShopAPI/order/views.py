from django.shortcuts import render
from rest_framework import generics
from rest_framework import mixins

from .models import *
from .serializers import OrderCreateSerializer
# Create your views here.

class OrderCreateView(mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OrderPatchView(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)