from django.urls import path
from .views import (Register, VerifyOTP, BecomeSeller, ApproveSeller, VendorProfile, CustomerProfile,
                    AdminGetAllVendors, AdminGetAllCustomers)

app_name = 'account'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('verify_otp/', VerifyOTP.as_view(), name='verify_otp'),
    path('become_seller/', BecomeSeller.as_view(), name='become_seller'),
    path('approve_seller/', ApproveSeller.as_view(), name='approve_seller'),
    path('vendor_profile/', VendorProfile.as_view(), name='vendor_profile'),
    path('customer_profile/', CustomerProfile.as_view(), name='customer_profile'),
    path('admin_getAll_vendors/', AdminGetAllVendors.as_view(), name='admin_getAll_vendors'),
    path('admin_getAll_customers/', AdminGetAllCustomers.as_view(), name='admin_getAll_customers'),
]
