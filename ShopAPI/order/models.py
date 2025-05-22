from uuid import uuid4

from django.db import models
from django.contrib.auth import get_user_model

from product.models import ProductItem
# Create your models here.

User = get_user_model()

class Order(models.Model):
    class OrderPayment(models.TextChoices):
        CARD = 'card'
        QR = 'QR'
        CASH = 'cash'

    class OrderDelivery(models.TextChoices):
        DELIVERY = 'delivery'
        PICKUP = 'pickup'

    class OrderStatus(models.TextChoices):
        PENDING = 'pending'
        PAID = 'paid'
        PROCESSING = 'processing'
        DELIVERED = 'delivered'
        CANCELLED = 'cancelled'
        REFUNDED = 'refunded'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(null=True, blank=True)
    total_price = models.FloatField()
    payment_method = models.CharField(choices=OrderPayment.choices, default=OrderPayment.CARD, max_length=4)
    delivery_method = models.CharField(choices=OrderDelivery.choices, default=OrderDelivery.PICKUP, max_length=8)
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.PENDING, max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_item = models.ForeignKey(ProductItem, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(null=True, blank=True)
    price_at_purchase = models.FloatField(null=True, blank=True)