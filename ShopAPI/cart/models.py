from django.db import models
from django.contrib.auth import get_user_model
from product.models import ProductItem
# Create your models here.
User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'session_key']

    def __str__(self):
        if self.user:
            return f'{self.user}'
        return f'{self.session_key}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'product_item']

    def __str__(self):
        return f'{self.product_item.product_id.name} x {self.amount}'
