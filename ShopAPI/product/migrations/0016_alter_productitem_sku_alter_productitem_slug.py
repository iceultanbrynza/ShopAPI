# Generated by Django 5.2 on 2025-05-01 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_productitem_sku_productitem_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='sku',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
