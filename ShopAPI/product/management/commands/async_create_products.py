import asyncio
import re
import aiohttp
import json
import time
import requests

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import connection

from ...models import Product, ProductItem, Category, AttributeOption, AttributeType, Image

sem = asyncio.Semaphore(10)

async def get_json(session, url):
    async with sem:
        async with session.get(url) as resp:
            return await resp.json()

async def get_all(session:aiohttp.ClientSession,
                  base_category_url:str,
                  base_product_url:str,
                  item_base_url:str,
                  devices:dict):

    cats = await get_json(session, url=base_category_url)

    product_tasks = {}
    for dev, count in devices.items():
        block = cats[{'iphone': 1, 'mac': 2, 'ipad': 3}[dev]]
        urls = [child['url'] for child in block['children'][:count]]
        product_tasks[dev] = [get_json(session, f"{base_product_url}/{url}") for url in urls]

    products = {}
    for dev, tasks in product_tasks.items():
        products[dev] = await asyncio.gather(*tasks)

    items = {}
    for dev, prods in products.items():
        items[dev] = {}
        for p in prods:
            slug = p['category']['slug']
            product_items:list = p['products']['data']
            item_tasks = [get_json(session, f"{item_base_url}/{product_item['url']}")
                                                               for product_item
                                                               in product_items]
            items[dev].setdefault(slug, []).extend(item_tasks)

    product_items_dict = {}
    for dev, product in items.items():
        product_items_dict[dev] = {}
        for slug, tasks in items[dev].items():
            results = await asyncio.gather(*tasks)
            product_items_dict[dev].setdefault(slug, {})
            for item_data in results:
                item_slug = item_data['product']['slug']
                product_items_dict[dev][slug][item_slug] = item_data

    return {'categories': cats, 'products': products, 'items': product_items_dict}

async def main(base_category_url:str,
               base_product_url:str,
               item_base_url:str,
               devices:dict):

    async with aiohttp.ClientSession() as session:
        data = await get_all(session,
                            base_category_url,
                            base_product_url,
                            item_base_url,
                            devices)
        return data

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        start = time.time()

        base_category_url = 'https://ispace.kz/api/catalog/categories'
        base_product_url = 'https://ispace.kz/api/almaty/apr/catalog/products/category'
        item_base_url = 'https://ispace.kz/api/apr/catalog/products'

        base_image_url = 'https://cdn0.ipoint.kz/AfrOrF3gWeDA6VOlDG4TzxMv39O7MXnF4CXpKUwGqRM/resize:fit:230/bg:fff/plain/s3://'
        ending = '@webp'

        devices = {'iphone': 11, 'mac': 3, 'ipad': 4}

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(
            main(base_category_url,
                 base_product_url,
                 item_base_url,
                 devices)
        )
        loop.close()

        # self.create_categories()
        # self.create_attributes_for_filtering()
        self.create_products(data['categories'], devices)
        self.create_product_items(data['products'], data['items'], base_image_url, ending)

        end = time.time()

        # with open('products.json', 'w') as f:
        #     json.dump(data['products'], f, ensure_ascii=False, indent=2)
        # with open('product_items.json', 'w') as f:
        #     json.dump(data['items'], f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.NOTICE(f'Время сбора данных: {end - start:.2f} секунд'))

    def reset_autoincrement(self, model):
        table_name = model._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")

    def create_categories(self):
        Category.objects.all().delete()
        self.reset_autoincrement(Category)
        Category.objects.create(slug='iphone', name='iPhone')
        Category.objects.create(slug='mac', name='Mac')
        Category.objects.create(slug='ipad', name='iPad')

    def create_attributes_for_filtering(self):
        storage = AttributeType(id='storage',type='storage')
        storage.save()
        display = AttributeType(id='display',type='display')
        display.save()
        ram = AttributeType(id='ram',type='RAM')
        ram.save()
        cpu = AttributeType(id='cpu',type='CPU')
        cpu.save()

    def create_products(self, cats, devices):
        blocks = {}
        for dev in ['iphone', 'mac', 'ipad']:
            index = {'iphone': 1, 'mac': 2, 'ipad': 3}[dev]
            json = cats[index]
            blocks[dev] = json
        for dev, block in blocks.items():
        # range to avoid non-required positions such as Services-for-<device>
            products = block['children'][:devices[dev]]
            self.instantiate_model(block, products)

    def instantiate_model(self, block, devices):
        for device in devices:
            slug = device['url'].split('/')[1]
            category_id = Category.objects.get(name=block['name'].split(' ')[0])
            name = device['name'].split(' в ')[0]
            discount = 0
            product = Product.objects.create(slug=slug,
                                            category_id=category_id,
                                            name=name,
                                            discount=discount)
            product.save()

    def download_and_attach_image(self, type:str, product_item, image_url, filename):
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image(type=type)
            image.save()
            product_item.image.add(image)
            image.image.save(filename, ContentFile(response.content), save=True)
        else:
            print(f"Не удалось скачать изображение: {image_url}")

    def create_product_items(self, products, product_items, base_image_url, ending):
        for dev in ['iphone', 'mac', 'ipad']:
            for product in products[dev]:
                product_slug = product['category']['slug']
                ProductObject = Product.objects.get(slug=product_slug)
                for data in product['products']['data']:
                    slug = data['slug']
                    sku = data['sku']
                    product_id = ProductObject
                    name = data['name']
                    color = data['name'].split(', ')[-1]
                    weight = data['weight']
                    price = float(data['prices']['price'])
                    discount = 0

                    item_data = product_items[dev][product_slug][slug] # - json

                    specification = item_data['product']['attributes']
                    availability = 1

                    try:
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
                    except:
                        continue
                    series = specification.get('Технические характеристики', {}).get('Серия и семейство')
                    self.add_attributes(dev, item_data, product_item, color, base_image_url, ending, series=series)

    def add_attributes(self, device:str, item_data, product_item: ProductItem, color, base_image_url, ending, series=None):
        category = Category.objects.get(slug=device)
        slug = product_item.product_id.slug

        config = item_data['product'].get('configuration', '')
        storage = config.split('  / ')[0] if '  / ' in config else config
        storage = storage.replace('GB', 'ГБ').replace('TB', 'ТБ')

        display = cpu = ram = filename = filename_base = None

        attributes = item_data['product'].get('attributes', {})
        print(attributes)
        # Пытаемся получить атрибуты, как у iPhone
        if 'Размер дисплея' in attributes.get('Экран', {}):
            display = attributes['Экран']['Размер дисплея']
            filename_base = f"{display.replace('\"', '')}/{color.replace(' ', '_')}"

        # Как у Mac
        elif 'Диагональ экрана' in attributes.get('Экран', {}) or 'Видимая диагональ экрана' in attributes.get('Экран', {}):
            display = attributes['Экран'].get('Диагональ экрана') or attributes['Экран'].get('Видимая диагональ экрана')
            cpu = attributes['Процессор']['Процессор']
            ram = attributes['Память'].get('Объём оперативной памяти') or attributes['Память'].get('Емкость установленной оперативной памяти')
            filename_base = f"{'_'.join(cpu.split()[:2])}/{display.replace('\"', '')}/{color.replace(' ', '_')}"

        elif series:
            filename_base = f"{series.replace(' ', '_')}/{color.replace(' ', '_')}"
        # else:
        #     print(f"[WARN] Не удалось определить тип устройства: {item_data['product'].get('title')}")
        #     return
        # Как у iPad


        if storage:
            storage_type = AttributeType.objects.get(type='storage')
            storage_option, _ = AttributeOption.objects.get_or_create(
                option_name=storage, type_id=storage_type, category_id=category
            )
            product_item.attribute.add(storage_option)

        if display:
            display_type = AttributeType.objects.get(type='display')
            display_option, _ = AttributeOption.objects.get_or_create(
                option_name=display, type_id=display_type, category_id=category
            )
            product_item.attribute.add(display_option)

        if cpu:
            cpu_type = AttributeType.objects.get(type='cpu')
            cpu_option, _ = AttributeOption.objects.get_or_create(
                option_name=cpu, type_id=cpu_type, category_id=category
            )
            product_item.attribute.add(cpu_option)

        if ram:
            ram_type = AttributeType.objects.get(type='ram')
            ram_option, _ = AttributeOption.objects.get_or_create(
                option_name=ram, type_id=ram_type, category_id=category
            )
            product_item.attribute.add(ram_option)

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
                filename = f'{type}/{filename_base}/{cnt}.jpg'
                image = f'{slug}/{filename}'
                image = Image.objects.filter(image=filename, type=type).first()
                if image is not None:
                    product_item.image.add(image)
                else:
                    image_url = base_image_url + url + ending
                    self.download_and_attach_image(type, product_item, image_url, filename)