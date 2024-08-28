from rest_framework import serializers

from B2B_charge_system.utils.exceptions import CreditRequestNotApprovedException, VendorRechargeCreditRequestException, \
    UserNotFoundException, VendorInsufficientBalanceException
from account.models import Customer, Vendor
from account.serializers import validate_phone
from .models import CreditRequest, Transaction
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger('django')


class VendorCreditRequestSerializer(serializers.Serializer):
    charge_amount = serializers.DecimalField(max_digits=10, decimal_places=3)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['user']
        charge_amount = validated_data.get('charge_amount')
        request_not_approved = CreditRequest.objects.filter(vendor=user.vendor, approved=False).exists()
        if request_not_approved:
            logger.error("your request is not approved")
            raise CreditRequestNotApprovedException()
        recharge_request = CreditRequest.objects.filter(vendor=user.vendor, approved=True).first()
        if recharge_request:
            if recharge_request.charge_amount / 2 < recharge_request.vendor.charge_amount:
                logger.error("You cannot apply again until your balance is less than half of the requested amount")
                raise VendorRechargeCreditRequestException()
        credit_request = CreditRequest.objects.create(vendor=user.vendor,
                                                      charge_amount=charge_amount,
                                                      )
        return credit_request


class ApproveCreditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = ['id']
        read_only_fields = ['created_at', 'vendor', 'charge_amount', 'approved', 'created_at']

    def update(self, instance, validated_data):
        instance.approved = True
        instance.approved_at = timezone.now()
        instance.save()
        return instance


class VendorChargeCustomerSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, validators=[validate_phone])
    charge_amount = serializers.DecimalField(max_digits=10, decimal_places=3)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['user']
        charge_amount = validated_data.get('charge_amount')
        customer = Customer.objects.select_for_update().filter(user__phone_number=validated_data.get('phone_number'),
                                                               user__role='customer').first()
        vendor = Vendor.objects.select_for_update().filter(id=user.vendor.id).first()
        if not customer:
            raise UserNotFoundException()
        if charge_amount > vendor.charge_amount:
            logger.error("You do not have enough balance to make this transaction.")
            raise VendorInsufficientBalanceException()
        create_transaction = Transaction.objects.create(
            vendor=vendor,
            charge_amount=charge_amount,
            customer=customer
        )
        vendor.charge_amount -= charge_amount
        vendor.save()
        logger.info("vendor charge withdraw successful")
        customer.charge_amount += charge_amount
        customer.save()
        logger.info("customer charge deposit successful")
        return create_transaction
