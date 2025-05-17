from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import action

from .models import Cart, CartItem
from .serializers import *
# Create your views here.

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=user)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        return self.queryset.filter(session_key=session_key)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CartReadSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CartCreateSerializer
        if self.action in ['change_amount']:
            return CartItemWriteSerializer

    @action(detail=True, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        cart = self.get_object()
        try:
            cart_item = cart.cart_items.get(id = item_id)
            cart_item.delete()
            return Response({"detail": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found in this cart"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='change_amount/(?P<item_id>[^/.]+)')
    def change_amount(self, request, pk=None, item_id=None):
        cart = self.get_object()
        cart_item = cart.cart_items.filter(id = item_id).first()
        if not cart_item:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemWriteSerializer(cart_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

