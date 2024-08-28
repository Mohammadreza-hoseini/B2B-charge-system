from rest_framework.exceptions import APIException


class OTPWrongException(APIException):
    status_code = 400
    default_detail = 'Otp code is not correct'
    default_code = 'wrong_otp_code'

    def get_full_details(self):
        return {'message': self.detail}


class UserNotFoundException(APIException):
    status_code = 400
    default_detail = 'User not found'
    default_code = 'user_not_found'

    def get_full_details(self):
        return {'message': self.detail}


class DuplicatePhoneNumberException(APIException):
    status_code = 400
    default_detail = 'The mobile number is duplicated.'
    default_code = 'duplicate_phone_number'

    def get_full_details(self):
        return {'message': self.detail}


class DuplicateBecomeSellerException(APIException):
    status_code = 400
    default_detail = 'Your request has already been registered.'
    default_code = 'duplicate_become_seller'

    def get_full_details(self):
        return {'message': self.detail}


class DuplicateApproveSellerException(APIException):
    status_code = 400
    default_detail = 'Vendor already approved.'
    default_code = 'duplicate_approve_seller'

    def get_full_details(self):
        return {'message': self.detail}


class NotApproveSellerException(APIException):
    status_code = 400
    default_detail = 'Your account not approved.'
    default_code = 'not_approve_seller'

    def get_full_details(self):
        return {'message': self.detail}


class CreditRequestNotApprovedException(APIException):
    status_code = 400
    default_detail = 'You have an unapproved request and you cannot send new credit request.'
    default_code = 'credit_request_not_approved'

    def get_full_details(self):
        return {'message': self.detail}


class VendorRechargeCreditRequestException(APIException):
    status_code = 400
    default_detail = 'You cannot apply again until your balance is less than half of the requested amount.'
    default_code = 'vendor_recharge_credit_request'

    def get_full_details(self):
        return {'message': self.detail}


class VendorInsufficientBalanceException(APIException):
    status_code = 400
    default_detail = 'You do not have enough balance to make this transaction.'
    default_code = 'insufficient_balance'

    def get_full_details(self):
        return {'message': self.detail}
