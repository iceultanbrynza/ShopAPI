from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Cart)

@admin.register(CartItem)
class ProductItemAdmin(admin.ModelAdmin):
    readonly_fields=('id',)