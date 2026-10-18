"""Search backends: Elasticsearch when configured, else a database fallback.

Each function returns (total_hits, [ids]) in relevance/recency order. The view
hydrates those ids from the database, so both backends share serialization.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from feed.models import Post

User = get_user_model()


def _slice_ids(queryset, offset, limit):
    total = queryset.count()
    ids = list(queryset.values_list("id", flat=True)[offset : offset + limit])
    return total, ids


def search_users(q, offset, limit):
    if settings.SEARCH_USE_ES:
        from .documents import UserDocument

        s = UserDocument.search().query(
            "multi_match",
            query=q,
            fields=["username^3", "full_name^2", "first_name", "last_name"],
            fuzziness="AUTO",
        )
        total = s.count()
        ids = [int(h.meta.id) for h in s[offset : offset + limit].execute()]
        return total, ids

    qs = (
        User.objects.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )
        .order_by("username")
    )
    return _slice_ids(qs, offset, limit)


def search_posts(q, offset, limit):
    if settings.SEARCH_USE_ES:
        from .documents import PostDocument

        s = PostDocument.search().query(
            "multi_match",
            query=q,
            fields=["content", "author.full_name", "author.username"],
            fuzziness="AUTO",
        )
        total = s.count()
        ids = [int(h.meta.id) for h in s[offset : offset + limit].execute()]
        return total, ids

    qs = (
        Post.objects.filter(
            Q(content__icontains=q)
            | Q(author__username__icontains=q)
            | Q(author__first_name__icontains=q)
            | Q(author__last_name__icontains=q)
        )
        .order_by("-created")
    )
    return _slice_ids(qs, offset, limit)
