from rest_framework import serializers

from .models import Cart, CartItem

from product.serializers import ShortProductItemSerializer
from product.models import ProductItem

class CartItemSerializer(serializers.ModelSerializer):
        product_item =  ShortProductItemSerializer()

        class Meta:
            model = CartItem
            fields = (
                'id',
                'cart',
                'product_item',
                'amount'
            )

class CartReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    session_key = serializers.CharField(read_only=True)
    cart_items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = (
            'id',
            'user',
            'session_key',
            'cart_items'
        )

class CartItemWriteSerializer(serializers.ModelSerializer):
    product_item = serializers.PrimaryKeyRelatedField(queryset=ProductItem.objects.all())
    class Meta:
        model = CartItem
        fields = ('id',
                'product_item',
                'amount')
        read_only_fields = ('id',)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Amount of Cart Items must be at least 1')
        return value

    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance

class CartCreateSerializer(serializers.ModelSerializer):
    cart_items = CartItemWriteSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'session_key', 'cart_items')
        read_only_fields = ('id', 'user', 'session_key')

    def create(self, validated_data):
        items_data = validated_data.pop('cart_items')
        print(validated_data)
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        if user:
            cart, _ = Cart.objects.get_or_create(user=user)
        else:
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        for item in items_data:
            product_item = item['product_item']
            amount = item['amount']
            cart_item, created = CartItem.objects.get_or_create(cart=cart,product_item=product_item)

            if created:
                cart_item.amount = amount
            else:
                cart_item.amount += amount
            cart_item.save()

        return cart