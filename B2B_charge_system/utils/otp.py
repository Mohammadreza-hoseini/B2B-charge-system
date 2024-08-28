import pyotp
from datetime import timedelta
from django.utils import timezone

OTP_VALIDITY_DURATION = 1  # OTP validity duration in minutes


def generate_otp_secret():
    """Generates a new OTP secret."""
    return pyotp.random_base32()


def generate_otp(secret):
    """Generates an OTP using the provided secret."""
    totp = pyotp.TOTP(secret, interval=300)
    return totp.now()


def verify_otp(secret, otp, otp_created_at):
    """Verifies the OTP provided against the secret and the creation time."""
    totp = pyotp.TOTP(secret, interval=300)
    current_time = timezone.now()
    # Check if OTP creation time is available and if it is within the validity duration
    if otp_created_at and (current_time - otp_created_at) > timedelta(minutes=OTP_VALIDITY_DURATION):
        return False
    # Verify the OTP
    return totp.verify(otp)
