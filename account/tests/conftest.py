import pytest

from account.models import User, Customer, Vendor
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import uuid


@pytest.fixture
def user_factory():
    def create_user(**kwargs):
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

    return create_user


@pytest.fixture
def authenticated_customer(user_factory):
    user = user_factory(role='customer')
    Customer.objects.create(user=user)  # Ensure that a Customer object is created
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def customer_factory(user_factory):
    def create_customer(**kwargs):
        user = user_factory(role='customer', **kwargs)
        Customer.objects.create(user=user)  # Ensure that a Customer object is created
        return user.customer

    return create_customer


@pytest.fixture
def authenticated_admin(user_factory):
    user = user_factory(role='admin')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client, user


@pytest.fixture
def vendor_factory(customer_factory):
    def create_vendor(approved=False, **kwargs):
        customer = customer_factory()
        vendor = Vendor.objects.create(seller=customer.user, approved=approved, **kwargs)
        return vendor

    return create_vendor
