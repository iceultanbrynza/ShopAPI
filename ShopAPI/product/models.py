from django.db import models

# Create your models here.
class AttributeType(models.Model):
    type = models.CharField(max_length=15)
    def __str__(self):
        return f"{self.type}"
    #display
class AttributeOption(models.Model):
    type_id = models.ForeignKey(AttributeType, on_delete=models.CASCADE, related_name='options')
    option_name = models.CharField(max_length=15, unique=True)
    def __str__(self):
        return f"{self.type_id.type}: {self.option_name}"

class Category(models.Model):
    id = models.AutoField(primary_key=True) #for internal connections
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=10)
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(unique=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    discount = models.PositiveSmallIntegerField(default=1)
    def __str__(self):
        return f"{self.name}"

class ProductItem(models.Model):
    id = models.AutoField(primary_key=True)

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')

    name = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    # memory = models.CharField(max_length=7)
    weight = models.CharField(max_length=7,blank=True, null=True)
    price = models.CharField(max_length=15)
    discount = models.PositiveSmallIntegerField(default=0)
    availability = models.PositiveSmallIntegerField(default=1)

    attribute = models.ManyToManyField(AttributeOption, related_name='product_items')
    specification = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"{self.name},{self.attribute.all()}"

# class ProductProperty(models.Model):
#     product_item_id = models.ForeignKey()