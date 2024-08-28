# import threading
# import pytest
# from rest_framework.test import APIClient
# from account.models import User, Vendor, Customer
# from transaction.models import CreditRequest, Transaction
# from django.utils import timezone
# from decimal import Decimal
# from rest_framework_simplejwt.tokens import RefreshToken
#
#
# @pytest.fixture
# def setup_users_and_vendors():
#     # Create users and vendors
#     vendor1 = User.objects.create_user(
#         phone_number='09125558585', username='09125558585', role='vendor', password='password'
#     )
#     vendor2 = User.objects.create_user(
#         phone_number='09126668585', username='09126668585', role='vendor', password='password'
#     )
#     vendor1_profile = Vendor.objects.create(seller=vendor1, name='Vendor 1', approved=True)
#     vendor2_profile = Vendor.objects.create(seller=vendor2, name='Vendor 2', approved=True)
#
#     # Create customers
#     customers = []
#     for i in range(1, 11):
#         user = User.objects.create_user(
#             phone_number=f'091200000{i:02d}', username=f'customer{i}', role='customer', password='password'
#         )
#         customer = Customer.objects.create(user=user)
#         customers.append(customer)
#
#     # Add some initial credit to vendors
#     vendor1_profile.charge_amount = Decimal('50000.00')  # Initial credit for testing
#     vendor2_profile.charge_amount = Decimal('50000.00')  # Initial credit for testing
#     vendor1_profile.save()
#     vendor2_profile.save()
#
#     return vendor1, vendor2, vendor1_profile, vendor2_profile, customers
#
#
# @pytest.fixture
# def auth_token():
#     def _auth_token(user):
#         refresh = RefreshToken.for_user(user)
#         return str(refresh.access_token)
#
#     return _auth_token
#
#
# def run_credit_requests(client, auth_token, vendor, num_requests):
#     token = auth_token(vendor)
#     for _ in range(num_requests):
#         response = client.post('/transactions/vendor_credit_request/', {
#             'charge_amount': 1000
#         }, HTTP_AUTHORIZATION=f'Bearer {token}')
#         assert response.status_code == 200
#         credit_request_id = response.data['id']
#         credit_request = CreditRequest.objects.get(id=credit_request_id)
#         credit_request.approved = True
#         credit_request.approved_at = timezone.now()
#         credit_request.save()
#
#
# def run_transactions(client, auth_token, vendor, customers, num_transactions):
#     token = auth_token(vendor)
#     for i in range(num_transactions):
#         customer = customers[i % len(customers)]  # Rotate through customers
#         response = client.post('/transactions/vendor_charge_customer/', {
#             'phone_number': customer.user.phone_number,
#             'charge_amount': 10
#         }, HTTP_AUTHORIZATION=f'Bearer {token}')
#         assert response.status_code == 200
#         Transaction.objects.create(
#             vendor=vendor,
#             customer=customer,
#             charge_amount=10
#         )
#
#
# @pytest.mark.django_db
# def test_credit_requests_and_transactions(setup_users_and_vendors, auth_token):
#     vendor1, vendor2, vendor1_profile, vendor2_profile, customers = setup_users_and_vendors
#
#     client = APIClient()  # Initialize APIClient
#
#     # Start threads for credit requests
#     thread1 = threading.Thread(target=run_credit_requests, args=(client, auth_token, vendor1, 10))
#     thread2 = threading.Thread(target=run_credit_requests, args=(client, auth_token, vendor2, 10))
#     thread1.start()
#     thread2.start()
#     thread1.join()
#     thread2.join()
#
#     # Start threads for transactions
#     thread3 = threading.Thread(target=run_transactions, args=(client, auth_token, vendor1, customers, 1000))
#     thread4 = threading.Thread(target=run_transactions, args=(client, auth_token, vendor2, customers, 1000))
#     thread3.start()
#     thread4.start()
#     thread3.join()
#     thread4.join()
#
#     # Check final balance for vendors
#     vendor1_profile.refresh_from_db()
#     vendor2_profile.refresh_from_db()
#
#     expected_vendor1_balance = Decimal('50000.00') + Decimal('1000') - Decimal('1000')
#     expected_vendor2_balance = Decimal('50000.00') + (Decimal('1000') * 10)  # Assuming no transactions with vendor2
#
#     assert vendor1_profile.charge_amount == expected_vendor1_balance
#     assert vendor2_profile.charge_amount == expected_vendor2_balance
#
#     print(f"Vendor 1 final balance: {vendor1_profile.charge_amount}")
#     print(f"Vendor 2 final balance: {vendor2_profile.charge_amount}")
