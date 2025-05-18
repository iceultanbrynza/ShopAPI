from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderCreateView.as_view()),
    path('<uuid:id>', views.OrderPatchView.as_view()),
]