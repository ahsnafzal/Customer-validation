from django.db import models

# Create your models here.
class Batch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")


class PendingCustomer(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    data = models.JSONField()