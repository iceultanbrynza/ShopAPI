import json, os, requests
from django.core.management.base import BaseCommand
from ...models import Product, ProductItem, Category, Image

# Introduction
# Core Idea: iPhones with the same color but different NVRAM have the same image
# so we want those iPhones to share the same Images and Image Model
# iPhones within the same Product share the same display size
# The same goes for iPads
# In case of Macs, only diagonal and color affect the photo.

# Example of Product URL Request from iSpace for iPhone:
# https://ispace.kz/api/almaty/apr/catalog/products/category/iphone/iphone-16-pro-max?iscorp=0

# Example of ProductItem URL Request from iSpace for iPhone:
# https://ispace.kz/api/apr/catalog/products/iphone/iphone-16-pro-max/iphone-16-pro-max-256-gb-black-titanium-mywv3hxa
# for iPad:
# https://ispace.kz/api/apr/catalog/products/ipad/ipad-pro/ipad-pro-11-4rd-gen-2-tb-wi-fi-seryy-kosmos-mnxm3rka
# for Mac:
# https://ispace.kz/api/apr/catalog/products/mac/macbook-pro/macbook-pro-162-32-gb-1-tb-apple-m1-max-seryy-kosmos-mk1a3rua

class Command(BaseCommand):
    help = 'Загружаем фотографии товаров'
    def handle(self, *args, **kwargs):

    def create_urls(self):
        base_url = 