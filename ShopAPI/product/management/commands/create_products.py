import json, os, requests
from django.core.management.base import BaseCommand
from ...models import Product, ProductItem, Category, AttributeOption

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        product_path = os.path.join(base_dir, 'dataset', 'product.json')
        iphones_path = os.path.join(base_dir, 'dataset', 'iphone_items')

        urls = self.create_urls(base_dir)

        with open(product_path, encoding='utf-8') as f:
            data1 = json.load(f)
        self.create_products(data1)
        for iphone in os.listdir(iphones_path):
            with open(os.path.join(iphones_path, iphone), encoding='utf-8') as f:
                data2 = json.load(f)
                self.create_product_items(data2, url=urls[data2['product']['category'][0]['slug']])

        self.stdout.write(self.style.SUCCESS('Продукты импортированы'))
    def create_urls(self, basedir)->dict:
        urls = {}

        path = os.path.join(basedir, 'dataset', 'iphone_items')

        for item in os.listdir(path):
            with open(os.path.join(path,item), 'r') as f:
                json_file = json.loads(f.read())
                slug = json_file['product']['category'][0]['slug']
                urls[slug]=('https://ispace.kz/api/aktau/apr/catalog/products/category/iphone/'+slug+'?iscorp=0')
        return urls

    def create_products(self,data):
        category_id = Category.objects.get(id=1)
        for child in data['categories']['children']:
            slug = child.get('slug', '')
            name = child.get('name', '')
            # url = child.get('url', '')
            discount = child.get('discount', 0)

            product = Product(category_id=category_id,
                            slug=slug,
                            name=name,
                            # url = url,
                            discount=discount)

            product.save()

    def create_product_items(self,item, url):
        # dataset/iphone_items are data for one particular model (models differs by color and memory)
        # from each group (iphone-16, iphone-16-pro, etc.). Since all iPhone models within one
        # group share the same characteristics, I used these data for retrieving characteristics.
        # the only thing that is differs from one model to another is memory.
        # price depends on memory only.
        # in order to obtain particular price for each possible memory that group could possibly have,
        # I use group data set, where it has 'data' about each model that belongs to this group
        # along with its memory and price

        product = item['product']

        slug = item['category']['slug']
        product_id = Product.objects.get(slug=slug)

        weight = product['weight']
        discount = 0
        availability = 1
        specification = product['attributes']
        display = specification['Дисплей']['Размер дисплея']
        del specification["Память"]

        data = requests.get(url)
        iphones:list = data.json()['products']['data']

        for iphone in iphones:
            name = iphone['name']
            memory = iphone['configuration']
            price = float(iphone['prices']['price'])

            # update
            item_slug = iphone['slug']
            sku = iphone['sku']

            try:
                color = iphone['name'].split(', ')[2]
            except:
                continue

            product_item = ProductItem(product_id=product_id,
                                slug=item_slug,
                                sku=sku,
                                name=name,
                                color=color,
                                weight=weight,
                                price=price,
                                discount=discount,
                                availability=availability,
                                specification=specification)

            product_item.save()

            try:
                memory_option = AttributeOption.objects.get(option_name=memory)
                display_option = AttributeOption.objects.get(option_name=display)
                product_item.attribute.add(memory_option, display_option)
            except:
                replacements = {
                    'GB': 'ГБ',
                    'TB': 'ТБ'}
                for latin, cyrillic in replacements.items():
                    memory = memory.replace(latin, cyrillic)
                memory_option = AttributeOption.objects.get(option_name=memory)
                display_option = AttributeOption.objects.get(option_name=display)
                product_item.attribute.add(memory_option, display_option)

#filter by Camera, Memory, Display
# delete only Memory block