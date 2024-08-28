import pytest

from B2B_charge_system.utils.exceptions import CreditRequestNotApprovedException, VendorRechargeCreditRequestException
from transaction.models import CreditRequest
from transaction.serializers import VendorCreditRequestSerializer
from account.models import Vendor, User
from decimal import Decimal


@pytest.fixture
def vendor_user():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=100.000)
    return vendor


@pytest.mark.django_db
def test_vendor_credit_request_serializer_creation(vendor_user):
    data = {'charge_amount': '200.000'}
    serializer = VendorCreditRequestSerializer(data=data, context={'user': vendor_user.seller})
    assert serializer.is_valid()
    credit_request = serializer.save()
    assert credit_request.vendor == vendor_user
    assert credit_request.charge_amount == Decimal('200.000')


@pytest.mark.django_db
def test_charge_amount_update(vendor_user):
    data = {'charge_amount': '300.000'}
    serializer = VendorCreditRequestSerializer(data=data, context={'user': vendor_user.seller})
    assert serializer.is_valid()
    credit_request = serializer.save()
    assert CreditRequest.objects.get(pk=credit_request.pk).charge_amount == Decimal('300.000')


@pytest.mark.django_db
def test_create_credit_request_success():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=0)
    user = MockUser(vendor=vendor)

    serializer = VendorCreditRequestSerializer(data={'charge_amount': '1000.000'}, context={'user': user})
    assert serializer.is_valid()
    credit_request = serializer.save()

    assert credit_request.charge_amount == 1000.000
    assert credit_request.vendor == vendor
    assert not credit_request.approved
    assert credit_request.vendor.charge_amount == 0


@pytest.mark.django_db
def test_create_credit_request_with_unapproved_request():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=0)
    user = MockUser(vendor=vendor)
    CreditRequest.objects.create(vendor=vendor, charge_amount=5000, approved=False)

    serializer = VendorCreditRequestSerializer(data={'charge_amount': '1000.000'}, context={'user': user})
    with pytest.raises(CreditRequestNotApprovedException):
        serializer.is_valid(raise_exception=True)
        serializer.save()


@pytest.mark.django_db
def test_create_credit_request_with_approved_request_high_balance():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=5000)
    user = MockUser(vendor=vendor)
    CreditRequest.objects.create(vendor=vendor, charge_amount=10000, approved=True)

    serializer = VendorCreditRequestSerializer(data={'charge_amount': '1000.000'}, context={'user': user})
    with pytest.raises(VendorRechargeCreditRequestException):
        serializer.is_valid(raise_exception=True)
        serializer.save()


@pytest.mark.django_db
def test_create_credit_request_with_approved_request_low_balance():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=1000)
    user = MockUser(vendor=vendor)
    CreditRequest.objects.create(vendor=vendor, charge_amount=5000, approved=True)
    vendor.charge_amount = 1000
    vendor.save()
    serializer = VendorCreditRequestSerializer(data={'charge_amount': '1000.000'}, context={'user': user})
    assert serializer.is_valid()
    credit_request = serializer.save()

    assert credit_request.charge_amount == 1000.000
    assert credit_request.vendor == vendor
    assert not credit_request.approved
    assert credit_request.vendor.charge_amount == 1000


class MockUser:
    def __init__(self, vendor):
        self.vendor = vendor
