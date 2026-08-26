from rest_framework.routers import DefaultRouter
from customers.views import  DownloadView, process_customer
from django.urls import path, include

urlpatterns = [
    path("download/", DownloadView.as_view()),
    path("process_customer/", process_customer , name="process"),
    
]
