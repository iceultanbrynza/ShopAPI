from django.urls import path
from .views import *

urlpatterns=[
    path('list/', AllProductsItemsByCategory.as_view()),
    path('<slug:slug>/', ProductItemsByCategory.as_view()),
    path('search', SearchProductItems.as_view())
]