from django.urls import path
from .views import VendorCreditRequest, ApprovedCreditRequest, VendorChargeCustomer

app_name = 'transaction'

urlpatterns = [
    path('vendor_credit_request/', VendorCreditRequest.as_view(), name='vendor_credit_request'),
    path('approved_credit_request/<uuid:pk>/', ApprovedCreditRequest.as_view(), name='approved_credit_request'),
    path('vendor_charge_customer/', VendorChargeCustomer.as_view(), name='vendor_charge_customer'),
]
