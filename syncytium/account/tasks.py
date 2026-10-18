from celery import shared_task
from core.utils import send_email
from decouple import config
from django.contrib.auth import get_user_model

from .utils import generate_email_verification_token

User = get_user_model()

FRONTEND_APP_URL = config("FRONTEND_APP_URL", "http://localhost:3000")
BACKEND_APP_URL = config("BACKEND_APP_URL", "http://localhost:8000")


@shared_task
def send_registration_email(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        print("Registration email not sent. User not found.")
        return
    subject = "Welcome to Orbit"
    message = (
        f"Hi {user.first_name}, welcome to Orbit! We are glad to have "
        f"you joined. Visit our app here: {FRONTEND_APP_URL}"
    )
    recipient_list = [user.email]
    send_email(subject, message, recipient_list)
    print(f"Registration email sent to {user.email}")


@shared_task
def send_email_verification_link_email(user_id, is_new=False):
    user = User.objects.filter(id=user_id).first()
    if not user:
        print("Email verification link email not sent. User not found.")
        return
    token = generate_email_verification_token(user_id)
    verification_link = f"{BACKEND_APP_URL}/account/verify-email/{token}/"
    subject = "Verify your email address"
    if is_new:
        message = (
            f"Hi {user.first_name}, verify your email address by clicking "
            f"this link: {verification_link}"
        )
    else:
        message = (
            f"Hi {user.first_name}, you have changed your email address. "
            f"Click this link to verify your email address: {verification_link}"
        )
    recipient_list = [user.email]
    send_email(subject, message, recipient_list)
    print(f"Email verification link email sent to {user.email}")
