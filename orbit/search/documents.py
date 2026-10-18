"""Elasticsearch documents for searchable models (users and posts)."""
from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from feed.models import Post

User = get_user_model()

# Shared single-node dev index settings.
INDEX_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}


@registry.register_document
class UserDocument(Document):
    """Indexes users for people search."""

    full_name = fields.TextField()

    class Index:
        name = "users"
        settings = INDEX_SETTINGS

    class Django:
        model = User
        fields = ["id", "username", "first_name", "last_name"]

    def prepare_full_name(self, instance):
        return f"{instance.first_name} {instance.last_name}".strip()


@registry.register_document
class PostDocument(Document):
    """Indexes posts for content search, with denormalized author info."""

    author = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "username": fields.TextField(),
            "full_name": fields.TextField(),
        }
    )

    class Index:
        name = "posts"
        settings = INDEX_SETTINGS

    class Django:
        model = Post
        fields = ["id", "content", "created"]
        # Re-index a post when its author changes.
        related_models = [User]

    def prepare_author(self, instance):
        a = instance.author
        return {
            "id": a.id,
            "username": a.username,
            "full_name": f"{a.first_name} {a.last_name}".strip() or a.username,
        }

    def get_queryset(self):
        return super().get_queryset().select_related("author")

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.posts.all()
        return None
