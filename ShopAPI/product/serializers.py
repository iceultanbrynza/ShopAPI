from rest_framework import serializers

from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'slug',
            'name'
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'slug',
            'name',
            'discount'
        )

class ProductItemSerializer(serializers.ModelSerializer):
    class AttributeOptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = AttributeOption
            fields = ('option_name',)

    # attribute_filter = serializers.SerializerMethodField()
    # attribute_sort = serializers.SerializerMethodField()
    configuration = serializers.SerializerMethodField()

    # def get_attribute_filter(self, obj):
    #     attrs = obj.attribute.values_list('type_id', flat=True).distinct()
    #     return attrs
    # def get_attribute_sort(self, obj):
    #     attrs = self.get_attribute_filter(obj)
    #     response = {}
    #     for attr in attrs:
    #         response[attr] = [option for option in AttributeOption.objects.values_list('option_name', flat=True).filter(type_id=attr)]
    #     return response
    def get_configuration(self, obj):
        return obj.attribute\
           .filter(type_id = 1)\
           .values_list('option_name', flat=True)\
           .first()

    class Meta:
        model = ProductItem
        fields = (
            'product_id',
            'name',
            'color',
            'configuration',
            # 'weight',
            'price',
            'discount',
            'availability',
            # 'specification'
        )

class HeaderFooterSerializer(serializers.ModelSerializer):
    iphones = serializers.SerializerMethodField()
    macs = serializers.SerializerMethodField()

    def get_iphones(self, obj):
        iphones = Product.objects.filter(category_id=1).values_list('name', flat=True)
        return list(iphones)

    def get_macs(self, obj):
        macs = Product.objects.filter(category_id=2).values_list('name', flat=True)
        return list(macs)

    class Meta:
        model = Product
        fields = (
            'iphones',
            'macs'
        )

class FilterSerializer(serializers.ModelSerializer):
    class OptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = AttributeOption
            fields = ('type_id', 'option_name')

    row = OptionSerializer(many=True, source='options')

    class Meta:
        model = AttributeType
        fields = ('id', 'type', 'row')
