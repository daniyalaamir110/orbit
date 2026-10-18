from secrets import token_hex

from .models import UserEmailStatus


def generate_email_verification_token(user_id):
    """Generate an email verification token for the user

    Operation:
        Whenever a user changes their email address, a new token is generated,
        and the previous token is invalidated.

    Args:
        `user_id` (`int`): The user ID
    
    Returns:
        `str`: The generated token
    """
    email_status = UserEmailStatus.objects.get_or_create(user_id=user_id)[0]
    email_status.verification_token = token_hex(16)
    email_status.is_verified = False
    email_status.save()
    return email_status.verification_token
