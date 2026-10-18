from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract model that provides self-updating `created` and 
    `modified` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RegistrationMethod(models.TextChoices):
    """Choices for the registration method"""
    EMAIL = "EM", "Email"
    GOOGLE = "GO", "Google"


class User(AbstractUser):
    """This model extends the default Django user model

    Details:
    * Overrides the email field and sets it as unique.
    * Adds a registration method field.
    """
    email = models.EmailField(unique=True, blank=False, null=False)
    registration_method = models.CharField(
        choices=RegistrationMethod.choices,
        default=RegistrationMethod.EMAIL,
        max_length=2,
    )

    def __str__(self):
        return self.username
    

class Privacy(models.TextChoices):
    """Choices for the privacy settings"""
    PUBLIC = "PU", "Public"
    FRIENDS_OF_FRIENDS = "FF", "Friends of Friends"
    FRIENDS = "FR", "Only Friends"
    CUSTOM = "CU", "Custom"    
    PRIVATE = "PR", "Private"


class PrivatizedModel(models.Model):
    """Abstract model that adds privacy setting to a model through 
    `privacy` field.
    """
    privacy = models.CharField(choices=Privacy.choices, default=Privacy.PUBLIC, max_length=2)
    custom_people = models.ManyToManyField(to=User, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.privacy != Privacy.CUSTOM:
            self.custom_people.clear()


class TokenMixin(models.Model):
    """Abstract model to handle token validity and verification status."""
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=32, blank=True)

    @property
    def is_token_valid(self):
        """Check if the verification token is valid."""
        if not self.is_verified and self.created:
            now = timezone.now()
            if (now - self.created).days < settings.TOKEN_VALIDITY:
                return True
        return False

    class Meta:
        abstract = True
