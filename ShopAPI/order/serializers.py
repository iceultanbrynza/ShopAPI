from rest_framework import serializers

from .models import Order, OrderItem
from product.models import ProductItem

class OrderItemWriteSerializer(serializers.ModelSerializer):
    product_item = serializers.PrimaryKeyRelatedField(queryset=ProductItem.objects.all())
    class Meta:
        model = OrderItem
        fields = (
            'product_item',
            'amount'
        )

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True) #accept only id's of ProductItem

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'items',
            'created_at',
            'phone_number',
            'address',
            'total_price',
            'payment_method',
            'delivery_method',
            'status'
        )
        read_only_fields = (
            'id',
            'user',
            'created_at',
            'total_price'
        )

    def validate(self, data):
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        if user is None:
            raise serializers.ValidationError('User must be authorized')

        print(data)
        delivery_method = data.get('delivery_method')
        address = data.get('address')

        if delivery_method == Order.OrderDelivery.PICKUP and not address:
            raise serializers.ValidationError('Address must be specified for pickup delivery method')

        return data

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        items = validated_data.pop('items')
        print(items)
        phone_number = validated_data.pop('phone_number')
        address = validated_data.pop('address', None)
        payment_method = validated_data.pop('payment_method')
        delivery_method = validated_data.pop('delivery_method')

        total_price = 0

        for item in items:
            product_item = item['product_item']
            total_price += product_item.price

        order = Order.objects.create(user=user,
                                    total_price=total_price,
                                    phone_number=phone_number,
                                    address=address,
                                    payment_method=payment_method,
                                    delivery_method=delivery_method)

        for item in items:
            product_item = item['product_item']
            price_at_purchase = float(product_item.price * (1 - product_item.discount/100))
            order_item = OrderItem.objects.create(order=order, **item, price_at_purchase=price_at_purchase)

        return order

    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)
        if items is not None:
            product_item_ids = [item['product_item'].id for item in items]
            OrderItem.objects.filter(order=instance).exclude(product_item__in=product_item_ids).delete()
            for item in items:
                product_item = item['product_item']
                amount = item['amount']
                order_item, _ = OrderItem.objects.get_or_create(order=instance,product_item=product_item)
                order_item.amount = amount
                order_item.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance