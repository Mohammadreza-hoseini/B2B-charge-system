from B2B_charge_system.utils.exception_handler import OncePerMinuteThrottle
from account.serializers import RegisterSerializer, VerifyOTPSerializer, BecomeSellerSerializer, \
    ApproveVendorSerializer, VendorSerializer, CustomerSerializer
from account.models import Vendor, Customer
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from B2B_charge_system.utils.permission_handler import CustomerPermission, VendorPermission


class Register(APIView):
    """
    API view to handle user registration.
    """

    # you should comment this section for pass all test
    throttle_classes = [OncePerMinuteThrottle]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)


class VerifyOTP(APIView):
    """
    API view to handle OTP verification.
    """

    # you should comment this section for pass all test
    throttle_classes = [OncePerMinuteThrottle]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)


class BecomeSeller(APIView):
    """
    API view to handle customer send request to become seller.
    """
    permission_classes = (IsAuthenticated, CustomerPermission,)

    def post(self, request, *args, **kwargs):
        additional_data = {'user': request.user}
        serializer = BecomeSellerSerializer(data=request.data, context=additional_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Your request has been sent and is waiting for the administrator approval',
                             'status_code': status.HTTP_200_OK, 'id': request.user.vendor.id},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveSeller(APIView):
    """
    API view to handle admin approve seller request.
    """
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request, *args, **kwargs):
        serializer = ApproveVendorSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Vendor confirmed',
                             'status_code': status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorProfile(APIView):
    permission_classes = (IsAuthenticated, VendorPermission,)

    def get(self, request, *args, **kwargs):
        serializer = VendorSerializer(request.user.vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfile(APIView):
    permission_classes = (IsAuthenticated, CustomerPermission,)

    def get(self, request, *args, **kwargs):
        serializer = CustomerSerializer(request.user.customer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminGetAllVendors(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, *args, **kwargs):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminGetAllCustomers(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
