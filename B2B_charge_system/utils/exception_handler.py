from rest_framework.throttling import UserRateThrottle

from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from .exceptions import DuplicatePhoneNumberException, OTPWrongException, UserNotFoundException, \
    DuplicateBecomeSellerException, DuplicateApproveSellerException, NotApproveSellerException, \
    CreditRequestNotApprovedException, VendorRechargeCreditRequestException, VendorInsufficientBalanceException


def custom_exception_handler(exc, context):
    """
    Custom exception handler for requests.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # General handling for custom exceptions
        if isinstance(exc, (
                DuplicatePhoneNumberException, OTPWrongException, UserNotFoundException, DuplicateBecomeSellerException,
                DuplicateApproveSellerException, NotApproveSellerException,
                CreditRequestNotApprovedException, VendorRechargeCreditRequestException,
                VendorInsufficientBalanceException
        )):
            response.data['message'] = response.data.pop('detail', '')

        # Specific handling for Throttled exceptions
        elif isinstance(exc, Throttled):
            wait_time = exc.wait
            response.data = {'message': f"Dear user please send request after {wait_time} seconds"}

        # Add status code to the response
        response.data['status_code'] = response.status_code

    return response


class OncePerMinuteThrottle(UserRateThrottle):
    """
    Custom throttle class allowing 5 requests per minute per user.
    """
    rate = '5/minute'
