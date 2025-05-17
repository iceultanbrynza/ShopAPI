import json
import os
import requests
import re

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from ...models import Product, ProductItem, Category, AttributeOption, AttributeType, Image

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        # self.create_attributes_for_filtering()
        # self.create_products()
        self.product_items_handler()

    def create_attributes_for_filtering(self):
        # storage = AttributeType(type='storage')
        # storage.save()
        # display = AttributeType(type='display')
        # display.save()
        ram = AttributeType(id='ram',type='RAM')
        ram.save()
        cpu = AttributeType(id='cpu',type='CPU')
        cpu.save()

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
            category_id = Category.objects.get(name=block['name'].split(' ')[0])
            name_list = re.findall(r'\b[a-zA-Z]+\b', device['name'])
            name = ' '.join(name_list)
            discount = 0
            product = Product.objects.create(slug=slug,
                                            category_id=category_id,
                                            name=name,
                                            discount=discount)
            product.save()

    def product_items_handler(self):
        base_url = 'https://ispace.kz/api/almaty/apr/catalog/products/category'
        item_base_url = 'https://ispace.kz/api/apr/catalog/products'
        base_image_url = 'https://cdn0.ipoint.kz/AfrOrF3gWeDA6VOlDG4TzxMv39O7MXnF4CXpKUwGqRM/resize:fit:230/bg:fff/plain/s3://'
        ending = '@webp'
        print('for mac:\n')
        self.create_product_items('mac',base_url,item_base_url,base_image_url,ending)
        # print('for ipad:\n')
        # self.create_product_items('ipad')

    def create_product_items(self, device:str, base_url, item_base_url, base_image_url, ending):
        urls = self.create_urls_for_product_items(base_url, device)
        print(urls)
        for slug, url in urls.items():
            product = Product.objects.get(slug=slug)
            response = requests.get(url).json()
            dataset = response['products']['data']
            for data in dataset:
                slug = data['slug']
                sku = data['sku']
                product_id = product
                name = data['name']
                color = data['name'].split(', ')[-1]
                weight = data['weight']
                price = float(data['prices']['price'])
                discount = 0

                # url inside that lead to product item card from product request
                # when all product items related to exact product are fetched
                url = item_base_url + '/' + data['url']
                print(url)
                print(requests.get(url))
                item_data = requests.get(url).json()
                specification = item_data['product']['attributes']
                availability = 1
                print(name + ' is fetched')
                #parse again using url from json for each item, because each
                # item even belonging to a single product has its own specification.
                product_item = ProductItem(
                    slug=slug,
                    sku=sku,
                    product_id=product_id,
                    name=name,
                    color=color,
                    weight=weight,
                    price=price,
                    discount=discount,
                    availability=availability,
                    specification=specification
                )
                product_item.save()
                print('product item is saved')
                if device == 'mac':
                    self.add_attributes_for_macs(item_data, product_item, product.slug, color,base_image_url, ending)
                if device == 'ipad':
                    self.add_attributes_for_ipads(item_data, product_item)

    def add_attributes_for_macs(self, item_data, product_item:ProductItem, product_slug, color, base_image_url, ending):
        # We need different function for Macs and iPads because they have
        # slightly different JSON's for attributes
        Mac = Category.objects.get(name='Mac')

        storage = item_data['product']['configuration']
        cpu = item_data['product']['attributes']['Процессор']['Процессор']

        try:
            ram = item_data['product']['attributes']['Память']['Объём оперативной памяти']
            display = item_data['product']['attributes']['Дисплей']['Диагональ экрана']
        except:
            ram = item_data['product']['attributes']['Память']['Емкость установленной оперативной памяти']
            display = item_data['product']['attributes']['Дисплей']['Видимая диагональ экрана']

        storage_type = AttributeType.objects.get(type='storage')
        display_type = AttributeType.objects.get(type='display')
        cpu_type=AttributeType.objects.get(type='cpu')
        ram_type=AttributeType.objects.get(type='ram')

        # Image Handling
        # Images can be assigned by groups: M1, M2, M3-M4.
        # The only attributes that affect the photo is color and display
        # memory, CPU do not affect
        # to save space we can reuse photos for a bunch of models
        images = {
            'thumbnail': [item_data['product']['image']],
            'gallery': item_data['product']['images']
        }
        for type, urls in images.items():
            cnt = 0
            for url in urls:
                cnt+=1
                if url is None:
                    break
                filename = f'{product_slug}/{type}/{'_'.join(cpu.split()[:2])}/{display.replace('"', '')}/{color.replace(' ', '_')}/{cnt}.jpg'
                # image = Image.objects.get(image=f'{product_slug}/{type}/{display}/{color}.jpg', type=type)
                image = Image.objects.filter(image=filename, type=type).first()
                print(image)
                if image is not None:
                    product_item.image.add(image)
                else:
                    image_url = base_image_url + url + ending
                    self.download_and_attach_image(type, product_item, image_url, f'{type}/{'_'.join(cpu.split()[:2])}/{display.replace('"', '')}/{color.replace(' ', '_')}/{cnt}.jpg')

        try:
            storage_option, _ = AttributeOption.objects.get_or_create(option_name=storage, type_id = storage_type, category_id=Mac)
            display_option, _ = AttributeOption.objects.get_or_create(option_name=display, type_id = display_type,category_id=Mac)
            cpu_option, _ = AttributeOption.objects.get_or_create(option_name=cpu, type_id = cpu_type,category_id=Mac)
            ram_option, _ = AttributeOption.objects.get_or_create(option_name=ram, type_id = ram_type,category_id=Mac)
            product_item.attribute.add(storage_option,
                                        display_option,
                                        cpu_option,
                                        ram_option)

        except:
            replacements = {
                'GB': 'ГБ',
                'TB': 'ТБ'}
            for latin, cyrillic in replacements.items():
                storage = storage.replace(latin, cyrillic)
            storage_option, _ = AttributeOption.objects.get_or_create(option_name=storage, type_id = storage_type,category_id=Mac)
            display_option, _ = AttributeOption.objects.get_or_create(option_name=display, type_id = display_type,category_id=Mac)
            cpu_option, _ = AttributeOption.objects.get_or_create(option_name=cpu, type_id = cpu_type,category_id=Mac)
            ram_option, _ = AttributeOption.objects.get_or_create(option_name=ram, type_id = ram_type,category_id=Mac)
            product_item.attribute.add(storage_option,
                                        display_option,
                                        cpu_option,
                                        ram_option)

    def download_and_attach_image(self, type:str, product_item, image_url, filename):
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image(type=type)
            image.save()
            product_item.image.add(image)
            image.image.save(filename, ContentFile(response.content), save=True)
        else:
            print(f"Не удалось скачать изображение: {image_url}")

    def add_attributes_for_ipads(self, item_data, product_item:ProductItem):
        iPad = Category.objects.get(name='iPad')
        storage = item_data['product']['configuration'].split('  / ')[0]
        storage_type = AttributeType.objects.get(type='storage')
        try:
            storage_option, _ = AttributeOption.objects.get_or_create(category_id=iPad,option_name=storage, type_id = storage_type)
            product_item.attribute.add(storage_option)
        except:
            replacements = {
                'GB': 'ГБ',
                'TB': 'ТБ'}
            for latin, cyrillic in replacements.items():
                storage = storage.replace(latin, cyrillic)
            storage_option, _ = AttributeOption.objects.get_or_create(category_id=iPad,option_name=storage, type_id = storage_type)
            product_item.attribute.add(storage_option)

    def create_urls_for_product_items(self, base_url, device:str)->dict:
        urls={}
        url = base_url + '/' + device
        products = Product.objects.filter(category_id__slug=device).values_list('slug', flat=True)
        for product in products:
            urls[product] = url + '/' + product
        return urls