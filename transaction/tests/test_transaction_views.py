import uuid

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from transaction.models import CreditRequest
from account.models import Vendor, User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


@pytest.fixture
def vendor_user():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=100.000)
    return vendor


@pytest.fixture
def user_factory():
    def create_admin(**kwargs):
        unique_number = str(uuid.uuid4().int)[:7]  # Convert to string and take first 7 digits
        unique_username = uuid.uuid4().hex[:10]  # Generate a unique username

        defaults = {
            'phone_number': f'0912{unique_number}',  # Generate a unique phone number
            'username': f'user_{unique_username}',  # Generate a unique username
            'role': 'customer',
            'is_active': True,
            'otp_secret': 'testsecret',
            'otp_created_at': timezone.now(),
        }

        # Check if the role is 'admin' and set is_staff and is_superuser accordingly
        if kwargs.get('role') == 'admin':
            defaults['is_staff'] = True
            defaults['is_superuser'] = True

        defaults.update(kwargs)
        return User.objects.create(**defaults)

    return create_admin


@pytest.fixture
def authenticated_admin(user_factory):
    user = user_factory(role='admin')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client, user


@pytest.mark.django_db
def test_vendor_credit_request_view(vendor_user):
    client = APIClient()
    client.force_authenticate(user=vendor_user.seller)
    url = reverse(
        'transaction:vendor_credit_request')
    data = {'charge_amount': '150.000'}

    response = client.post(url, data, format='json')
    assert response.status_code == 200
    assert CreditRequest.objects.filter(vendor=vendor_user, charge_amount=150).exists()


@pytest.mark.django_db
def test_approved_credit_request_view(authenticated_admin, vendor_user):
    client, admin = authenticated_admin
    credit_request = CreditRequest.objects.create(vendor=vendor_user, charge_amount=100)
    url = reverse('transaction:approved_credit_request', args=[credit_request.pk])

    response = client.put(url, format='json')
    assert response.status_code == 200
    credit_request.refresh_from_db()
    assert credit_request.approved is True
    assert credit_request.approved_at is not None
