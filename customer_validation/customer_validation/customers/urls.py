from rest_framework.routers import DefaultRouter
from customers.views import customer_list
from django.urls import path, include


urlpatterns=[
    path("", customer_list, name="customer_list"),
]