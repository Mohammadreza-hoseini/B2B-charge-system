from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class IdBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class ChargeAmountBaseModel(models.Model):
    charge_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class User(AbstractUser, IdBaseModel):
    Roles = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=Roles)
    phone_number = models.CharField(max_length=11, unique=True)
    otp_secret = models.CharField(max_length=32, null=True, blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone_number} - {self.username} - {self.role}"

    class Meta:
        ordering = ['phone_number']
        indexes = [
            models.Index(fields=['phone_number']),
        ]


class Customer(IdBaseModel, ChargeAmountBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')

    def __str__(self):
        return f"{self.user.phone_number} - {self.charge_amount}"


class Vendor(IdBaseModel, ChargeAmountBaseModel):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
    name = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seller.phone_number} - {self.name} - {self.approved} - {self.charge_amount}"
