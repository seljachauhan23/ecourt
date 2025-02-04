from django.db import models
from cases.models import *

class Payment(models.Model):
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=500)
    lawyer_email = models.EmailField()
    citizen_email = models.EmailField()
    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=50)
    signature = models.CharField(max_length=256)
    refund_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=100, choices=[(
        'Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending')
    requested_at = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True)
    paid_at = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True)
    proceed = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment - {self.order_id} for {self.email}"
