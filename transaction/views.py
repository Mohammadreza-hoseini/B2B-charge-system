from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from B2B_charge_system.utils.permission_handler import VendorPermission
from transaction.models import CreditRequest
from transaction.serializers import VendorCreditRequestSerializer, ApproveCreditRequestSerializer, \
    VendorChargeCustomerSerializer
import logging

logger = logging.getLogger('django')


class VendorCreditRequest(APIView):
    """
    API view to handle vendor credit request.
    """
    permission_classes = (IsAuthenticated, VendorPermission,)

    def post(self, request, *args, **kwargs):
        additional_data = {'user': request.user}
        serializer = VendorCreditRequestSerializer(data=request.data, context=additional_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'message': 'Your credit increase request has been registered and'
                           ' will be added to your panel after admin approval',
                'status_code': status.HTTP_200_OK, 'id': serializer.instance.id},
                status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovedCreditRequest(APIView):
    """
    API view to handle admin approve credit request.
    """
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get_object(self, pk):
        return get_object_or_404(CreditRequest, pk=pk)

    def put(self, request, pk):
        charge_request = self.get_object(pk)
        serializer = ApproveCreditRequestSerializer(charge_request, data=request.data)
        if serializer.is_valid():
            if charge_request.approved:
                logger.error("This request has already been approved.")
                return Response({'detail': 'This request has already been approved.'},
                                status=status.HTTP_400_BAD_REQUEST)
            logger.info("vendor account charged successfully.")
            serializer.save()
            return Response(serializer.data)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorChargeCustomer(APIView):
    """
    API view to handle vendor charge customer.
    """
    permission_classes = (IsAuthenticated, VendorPermission,)

    def post(self, request, *args, **kwargs):
        additional_data = {'user': request.user}
        serializer = VendorChargeCustomerSerializer(data=request.data, context=additional_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info("customer charged successfully.")
            return Response({
                'message': 'The charge was deposited into the customer account',
                'status_code': status.HTTP_200_OK},
                status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
