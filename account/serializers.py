import re
from account.models import User, Customer, Vendor
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from B2B_charge_system.utils.otp import generate_otp_secret, generate_otp, verify_otp
from B2B_charge_system.utils.exceptions import DuplicatePhoneNumberException, UserNotFoundException, OTPWrongException, \
    DuplicateBecomeSellerException, DuplicateApproveSellerException, NotApproveSellerException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'role', 'is_active',)


def validate_phone(phone):
    if not re.match(r"^09\d{9}$", phone):
        raise ValidationError("phone number is not valid.")


class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone])
    """
    0 means -> customer and 1 means -> vendor and 2 means -> admin
    """
    role = serializers.ChoiceField(choices=[0, 1, 2])

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        role = validated_data.get('role')
        otp_secret = generate_otp_secret()
        otp = generate_otp(otp_secret)
        otp_created_at = timezone.now()
        if role == 0:
            try:
                user, created = User.objects.get_or_create(phone_number=phone_number, username=phone_number,
                                                           role='customer')
                user.otp_secret = otp_secret
                user.otp_created_at = otp_created_at
                user.save()
            except IntegrityError:
                raise DuplicatePhoneNumberException()

        elif role == 1:
            vendor = User.objects.filter(phone_number=phone_number, username=phone_number, role='vendor').first()
            if not vendor:
                raise UserNotFoundException()
            elif not vendor.vendor.approved:
                raise NotApproveSellerException()
            else:
                vendor.otp_secret = otp_secret
                vendor.otp_created_at = otp_created_at
                vendor.save()
        elif role == 2:
            try:
                user = User.objects.get(phone_number=phone_number, role='admin')
                user.otp_secret = otp_secret
                user.otp_created_at = otp_created_at
                user.save()
            except ObjectDoesNotExist:
                raise UserNotFoundException()
        # Here you should send the OTP to the user's phone number
        # For demonstration purposes, we just return it in the response
        return {'otp': otp, 'status_code': status.HTTP_200_OK}


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise UserNotFoundException()

        if not verify_otp(user.otp_secret, otp, user.otp_created_at):
            raise OTPWrongException()
        return data

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        user = User.objects.get(phone_number=phone_number)
        if user.role == 'customer':
            Customer.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'status_code': status.HTTP_201_CREATED
        }


class BecomeSellerSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['user']
        get_duplicated_req = Vendor.objects.filter(seller=user).exists()
        if get_duplicated_req:
            raise DuplicateBecomeSellerException()
        vendor = Vendor.objects.create(seller=user, name=validated_data.get('name'))
        return vendor


class ApproveVendorSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)

    @transaction.atomic
    def create(self, validated_data):
        vendor_id = validated_data.get('id')
        vendor = Vendor.objects.filter(id=vendor_id).first()

        if not vendor:
            raise UserNotFoundException()
        if vendor.approved:
            raise DuplicateApproveSellerException()
        vendor.seller.customer.delete()
        vendor.seller.role = 'vendor'
        vendor.approved = True
        vendor.seller.save()
        vendor.save()
        return vendor


class VendorSerializer(serializers.ModelSerializer):
    vendor_detail = UserSerializer(source='seller')

    class Meta:
        model = Vendor
        fields = ('id', 'charge_amount', 'created_at', 'name', 'approved', 'vendor_detail',)


class CustomerSerializer(serializers.ModelSerializer):
    customer_detail = UserSerializer(source='user')

    class Meta:
        model = Customer
        fields = ('id', 'charge_amount', 'created_at', 'customer_detail',)
