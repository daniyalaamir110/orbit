"""Notification model: who did what on which post, for a recipient."""
from django.conf import settings
from django.db import models

from core.models import TimeStampedModel

User = settings.AUTH_USER_MODEL


class Notification(TimeStampedModel):
    """A notification raised for `recipient` by `actor` (e.g. a like/comment)."""

    class Verb(models.TextChoices):
        LIKE = "LI", "liked your post"
        COMMENT = "CO", "commented on your post"
        FOLLOW = "FO", "started following you"

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="+"
    )
    verb = models.CharField(max_length=2, choices=Verb.choices)
    post = models.ForeignKey(
        "feed.Post", on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["recipient", "is_read"])]

    def __str__(self):
        return f"{self.actor} {self.get_verb_display()} -> {self.recipient}"

    @classmethod
    def push(cls, *, recipient, actor, verb, post=None):
        """Create a notification, skipping self-directed ones."""
        if recipient == actor:
            return None
        return cls.objects.create(
            recipient=recipient, actor=actor, verb=verb, post=post
        )
