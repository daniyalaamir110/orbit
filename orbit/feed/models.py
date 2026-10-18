"""Feed models: posts, comments and likes."""
from django.conf import settings
from django.db import models

from core.models import TimeStampedModel

User = settings.AUTH_USER_MODEL


class Post(TimeStampedModel):
    """A single feed post authored by a user."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.author} · {self.content[:40]}"


class Comment(TimeStampedModel):
    """A comment on a post."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"{self.author} on {self.post_id}"


class Like(TimeStampedModel):
    """A like on a post. A user may like a post at most once."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"], name="unique_post_like"
            )
        ]

    def __str__(self):
        return f"{self.user} likes {self.post_id}"
