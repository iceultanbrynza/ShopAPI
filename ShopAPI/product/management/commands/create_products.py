import json, os
from django.core.management.base import BaseCommand
from ...models import Product, ProductItem, Category

# class ProductItem(models.Model):
#     id = models.AutoField(primary_key=True)

#     product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

#     color = models.CharField(max_length=10)
#     memory = models.PositiveSmallIntegerField(default=128)
#     price = models.PositiveIntegerField()
#     discount = models.PositiveSmallIntegerField(default=0)
#     availability = models.PositiveSmallIntegerField(default=1)

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        product_path = os.path.join(base_dir, 'dataset', 'product.json')
        item_path = os.path.join(base_dir, 'dataset', 'product_item.json')
        with open(product_path, encoding='utf-8') as f:
            data1 = json.load(f)
        with open(item_path, encoding='utf-8') as f:
            data2 = json.load(f)
        self.create_products(data1)
        self.create_product_items(data2)
        self.stdout.write(self.style.SUCCESS('Продукты импортированы'))
    def create_products(data):
        category_id = Category.objects.get(id=1)
        for child in data['categories']['children']:
            slug = child.get('slug', '')
            name = child.get('name', '')
            url = child.get('url', '')
            discount = child.get('discount', 0)
            product = Product(category_id=category_id,
                            slug=slug,
                            name=name,
                            url = url,
                            discount=discount)
            product.save()
    def create_product_items(items):
        for item in items['products']['data']:
            name = item['name']
            color = item['name'].split(', ')[2]
            memory = item['configuration']
            weight = item['weight']
            price =
            discount =
            availability = 