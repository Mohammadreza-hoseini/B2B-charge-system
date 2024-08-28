import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from account.models import User
from transaction.models import Vendor, Customer, Transaction


@pytest.mark.django_db
class TestVendorChargeCustomer:

    @pytest.fixture
    def setup_data(self):
        # create vendor and customer for test
        vendor_user = User.objects.create_user(username='vendor_user', password='vendor_pass', role='vendor')
        customer_user = User.objects.create_user(username='customer_user', password='customer_pass',
                                                 phone_number='09123447421', role='customer')

        vendor = Vendor.objects.create(seller=vendor_user, charge_amount=1000)
        customer = Customer.objects.create(user=customer_user, charge_amount=0)

        return {
            'vendor': vendor,
            'customer': customer,
            'vendor_user': vendor_user,
            'customer_user': customer_user,
        }

    def test_successful_charge(self, setup_data):
        client = APIClient()
        vendor_user = setup_data['vendor_user']
        client.force_authenticate(user=vendor_user)

        data = {
            'phone_number': '09123447421',
            'charge_amount': 100,
        }

        response = client.post(reverse('transaction:vendor_charge_customer'), data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'The charge was deposited into the customer account'

        assert Transaction.objects.filter(vendor=setup_data['vendor'], customer=setup_data['customer']).exists()

        setup_data['vendor'].refresh_from_db()
        setup_data['customer'].refresh_from_db()
        assert setup_data['vendor'].charge_amount == 900
        assert setup_data['customer'].charge_amount == 100

    def test_customer_not_found(self, setup_data):
        client = APIClient()
        vendor_user = setup_data['vendor_user']
        client.force_authenticate(user=vendor_user)

        data = {
            'phone_number': '09123448585',  # phone number does not exist
            'charge_amount': 100,
        }

        response = client.post(reverse('transaction:vendor_charge_customer'), data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'User not found' in str(response.data)

    def test_vendor_insufficient_balance(self, setup_data):
        client = APIClient()
        vendor_user = setup_data['vendor_user']
        client.force_authenticate(user=vendor_user)

        data = {
            'phone_number': '09123447421',
            'charge_amount': 2000,
        }

        response = client.post(reverse('transaction:vendor_charge_customer'), data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'You do not have enough balance to make this transaction.' in str(response.data)
