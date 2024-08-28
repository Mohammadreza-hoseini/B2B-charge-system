from account.models import IdBaseModel, ChargeAmountBaseModel, Vendor, Customer
from django.db import models
from django.db import transaction


class CreditRequest(IdBaseModel, ChargeAmountBaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING, related_name='credit_requests')
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Vendor: {self.vendor.name} - Approved: {self.approved} - ChargeAmount: {self.charge_amount}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous_approved = False
            if self.pk:
                try:
                    previous = CreditRequest.objects.select_for_update().get(pk=self.pk)
                    previous_approved = previous.approved
                except CreditRequest.DoesNotExist:
                    previous_approved = False
            if self.approved and not previous_approved:
                self.vendor.charge_amount += self.charge_amount
                self.vendor.save()
            super(CreditRequest, self).save(*args, **kwargs)


class Transaction(IdBaseModel, ChargeAmountBaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING, related_name='vendor_transactions')
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='customer_transactions')

    def __str__(self):
        return f"Vendor: {self.vendor.name} - Customer: {self.customer} - ChargeAmount: {self.charge_amount}"
