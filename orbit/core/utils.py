from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail


def validate_country_and_city(country, city):
    """Validate country and city.

    Operations:
    - If the country is not provided, use the country of the city.
    - If country is provided, check if the city belongs to the country.

    Args:
        `country` (`Country`): Country object.
        `city` (`City`): City object.

    Returns:
        `Country`, `City`: Country and City objects.

    Raises:
    - `ValidationError`: If the city does not belong to the country.
    """

    if not country:
        country = city.country
    elif city.country != country:
        raise ValidationError("City does not belong to the country")
    return country, city


def send_email(subject="", message="", recipient_list=[]):
    """Utility function to send an email.

    Operations:
    - Use the default email host user as the sender.
    - Send an email with the provided subject, message, and recipient list.

    Args:
        `subject` (`str`): Email subject.
        `message` (`str`): Email message.
        `recipient_list` (`list`): List of email recipients.

    Returns:
        `int`: Number of emails sent.
    """
    from_email = settings.EMAIL_HOST_USER
    sent = send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    return sent
