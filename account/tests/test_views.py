import uuid

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from account.models import User, Vendor, Customer
from B2B_charge_system.utils.otp import generate_otp
from django.utils import timezone


@pytest.mark.django_db
def test_register_customer():
    client = APIClient()
    url = reverse('account:register')
    data = {
        "phone_number": "09123456789",
        "role": 0  # Customer role
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'otp' in response.data
    assert User.objects.filter(phone_number=data['phone_number']).exists()


@pytest.mark.django_db
def test_verify_otp_for_customer(user_factory):
    # First, register the user to generate OTP
    user = user_factory(phone_number="09123456789", role='customer')
    user.otp_secret = "testsecret"
    user.otp_created_at = timezone.now()
    user.save()

    otp = generate_otp(user.otp_secret)  # use the same function as in your serializers
    client = APIClient()
    url = reverse('account:verify_otp')
    data = {
        "phone_number": user.phone_number,
        "otp": otp
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert Customer.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_become_seller(authenticated_customer):
    client, user = authenticated_customer
    url = reverse('account:become_seller')
    data = {
        "name": "Test Vendor"
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert Vendor.objects.filter(seller=user).exists()


@pytest.mark.django_db
def test_approve_seller(authenticated_admin, customer_factory):
    client, admin = authenticated_admin

    customer = customer_factory()
    vendor = Vendor.objects.create(seller=customer.user, name="Test Vendor")

    # check vendor approved or not
    assert not vendor.approved
    assert vendor.seller.role == 'customer'

    # admin confirm vendor request
    url = reverse('account:approve_seller')
    data = {"id": vendor.id}
    response = client.post(url, data, format='json')

    # check status code
    assert response.status_code == status.HTTP_200_OK

    # update vendor data from database
    vendor.refresh_from_db()

    # check vendor approved and role change to vendor
    assert vendor.approved
    assert vendor.seller.role == 'vendor'

    # check customer does not exist
    assert not Customer.objects.filter(user=vendor.seller).exists()


@pytest.mark.django_db
def test_approve_vendor_invalid_id(authenticated_admin):
    client, admin = authenticated_admin
    invalid_id = uuid.uuid4()  # create invalid uuid

    url = reverse('account:approve_seller')
    data = {
        "id": invalid_id
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User not found" in response.data['message']


@pytest.mark.django_db
def test_approve_vendor_already_approved(authenticated_admin, vendor_factory):
    client, admin = authenticated_admin
    vendor = vendor_factory(approved=True)  # Vendor approved

    url = reverse('account:approve_seller')
    data = {
        "id": vendor.id
    }
    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Vendor already approved" in response.data['message']
