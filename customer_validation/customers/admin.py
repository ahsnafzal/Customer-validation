from django.contrib import admin
from .models import Batch, PendingCustomer

admin.site.register(Batch)
admin.site.register(PendingCustomer)