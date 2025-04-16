from django.db import models

# Create your models here.

class Category(models.Model):
    id = models.AutoField(primary_key=True) #for internal connections
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=10)

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(unique=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    discount = models.PositiveSmallIntegerField(default=1)

class ProductItem(models.Model):
    id = models.AutoField(primary_key=True)

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    color = models.CharField(max_length=10)
    memory = models.CharField(max_length=7)
    weight = models.CharField(max_length=7)
    price = models.PositiveIntegerField()
    discount = models.PositiveSmallIntegerField(default=0)
    availability = models.PositiveSmallIntegerField(default=1)
