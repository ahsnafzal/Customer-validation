from rest_framework.routers import DefaultRouter
from customers.views import  download, upload_validate
from django.urls import path, include

urlpatterns = [
    path("download/", download, name="download"),
    path("upload_validate/", upload_validate, name="upload_validate"),
    
]
