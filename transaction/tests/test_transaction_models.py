import pytest
from django.utils import timezone
from transaction.models import CreditRequest
from account.models import Vendor, User


@pytest.fixture
def vendor():
    user = User.objects.create_user(username='testvendor', phone_number='09123456789', role='vendor')
    vendor = Vendor.objects.create(seller=user, name='Test Vendor', charge_amount=100.000)
    return vendor


@pytest.fixture
def credit_request(vendor):
    return CreditRequest.objects.create(vendor=vendor, charge_amount=100)


@pytest.mark.django_db
def test_credit_request_creation(vendor, credit_request):
    credit_request = CreditRequest.objects.create(vendor=vendor, charge_amount=100)
    assert credit_request.vendor == vendor
    assert credit_request.charge_amount == 100
    assert credit_request.approved is False
    assert credit_request.approved_at is None


@pytest.mark.django_db
def test_credit_request_approval(vendor, credit_request):
    credit_request = CreditRequest.objects.create(vendor=vendor, charge_amount=100)
    credit_request.approved = True
    credit_request.approved_at = timezone.now()
    credit_request.save()

    vendor.refresh_from_db()
    assert vendor.charge_amount == 200
    assert credit_request.approved is True
    assert credit_request.approved_at is not None


@pytest.mark.django_db
def test_save_no_previous_requests(vendor):
    credit_request = CreditRequest(vendor=vendor, charge_amount=100)
    credit_request.save()
    assert CreditRequest.objects.count() == 1
