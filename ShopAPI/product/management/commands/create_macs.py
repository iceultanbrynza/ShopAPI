import json, os, requests
from django.core.management.base import BaseCommand
from ...models import Product, ProductItem, Category, AttributeOption

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        self.create_products()

    def create_products(self):
        base_url = 'https://ispace.kz/api/catalog/categories'
        response = requests.get(base_url).json()
        mac_block = response[2]
        ipad_block = response[3]

        # range to avoid non-required positions such as Services-for-<device>
        macs = mac_block['children'][:3]
        ipads = ipad_block['children'][:4]

        self.instantiate_model(mac_block, macs)
        self.instantiate_model(ipad_block, ipads)

    def instantiate_model(self, block, devices):
        for device in devices:
            slug = device['url'].split('/')[1]
            category_id = block['name'].replace('в Алматы', '')
            name = device['name'].replace('в Алматы', '')
            discount = 0
            product = Product.objects.create(slug=slug,
                                            category_id=category_id,
                                            name=name,
                                            discount=discount)
            product.save()

    def create_product_items(self):
        