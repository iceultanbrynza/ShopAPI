from django.urls import path
from .views import *

urlpatterns=[
    path('catalogue/', SearchAndFilterProductItems.as_view()),
    path('<slug:slug>/', ProductByCategory.as_view()),
    path('<slug:product_slug>/<slug:item_slug>', RetrieveProductItem.as_view())
]