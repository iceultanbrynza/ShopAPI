# Generated by Django 5.2 on 2025-05-09 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_alter_productitem_sku_alter_productitem_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='sku',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='productitem',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
