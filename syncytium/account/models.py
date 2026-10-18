"""Account Models"""
from django.contrib.auth import get_user_model
from django.db import models

from core.models import PrivatizedModel, TimeStampedModel, TokenMixin


User = get_user_model()


class Follow(TimeStampedModel):
    """A directed follow relationship between two users."""
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            )
        ]

    def __str__(self):
        return f"{self.follower} → {self.following}"


class UserEmailStatus(TimeStampedModel, TokenMixin):
    """This model stores the user email status"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="email_status"
    )

    def __str__(self):
        return f"{self.user.username} email status"

    class Meta:
        verbose_name_plural = "User email statuses"


class Gender(models.TextChoices):
    """Choices for user's gender"""
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class UserProfile(TimeStampedModel):
    """This model stores the user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    gender = models.CharField(choices=Gender.choices, max_length=1, blank=True)

    def __str__(self):
        return self.user.username


class UserBirthDate(TimeStampedModel, PrivatizedModel):
    """This model stores the user's birth date"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_birth_date")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date of birth")


class UserLink(TimeStampedModel, PrivatizedModel):
    """This model stores the user's links"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_links")
    link = models.URLField(blank=True)


class UserPhone(TimeStampedModel, PrivatizedModel):
    """This model stores the user's links. Only one phone can be set
    as primary.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_phones")
    phone = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            UserPhone.objects.filter(user=self.user, is_primary=True) \
                .exclude(pk=self.pk).update(is_primary=False)


class UserAvatar(TimeStampedModel, PrivatizedModel):
    """This model stores the user's avatar image"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_avatar")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date of birth")


class UserAddress(TimeStampedModel, PrivatizedModel):
    """This model stores the user address"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address")
    country = models.ForeignKey(
        "cities_light.Country", on_delete=models.SET_NULL, null=True, blank=True
    )
    city = models.ForeignKey(
        "cities_light.City", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "User addresses"

    def __str__(self):
        return f"{self.user.username} – {self.city}, {self.country}"


class UserEducation(TimeStampedModel, PrivatizedModel):
    """This model stores the user education information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="educations")
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, verbose_name="Field of study")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} studied {self.field_of_study} at {self.school}"


class UserWorkExperience(TimeStampedModel, PrivatizedModel):
    """This model stores the user work experience information"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="work_experiences"
    )
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} worked as a {self.position} at {self.company}"
