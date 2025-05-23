from django_filters import FilterSet, CharFilter
from .models import *

class ProductItemFilter(FilterSet):
    class Meta:
        model = ProductItem
        fields = {
            'price': ['exact', 'range']
        }
    # pseudo-fields:
    pfilter = CharFilter(method='primary_filter')
    storage = CharFilter(method='filter_storage')
    display = CharFilter(method='filter_display')
    ram = CharFilter(method='filter_ram')
    cpu = CharFilter(method='filter_cpu')

    def primary_filter(self, queryset, name, value):
        return queryset.select_related('product_id', 'product_id__category_id').filter(product_id__category_id__slug = value)

    def filter_storage(self, queryset, name, value):
        return queryset.filter(attribute__type_id = 'storage',
                                attribute__option_name = value)

    def filter_display(self, queryset, name, value):
        return queryset.filter(attribute__type_id = 'display',
                                attribute__option_name = value)

    def filter_ram(self, queryset, name, value):
        return queryset.filter(attribute__type_id = 'ram',
                                attribute__option_name = value)

    def filter_cpu(self, queryset, name, value):
        return queryset.filter(attribute__type_id = 'cpu',
                                attribute__option_name = value)