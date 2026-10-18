"""Elasticsearch-backed search with All / Users / Posts tabs.

ES ranks and matches; the matching ids are then hydrated from the database so
post results carry live like/comment counts and the viewer's like state, and
user results are real model instances.
"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from feed.models import Like, Post
from feed.serializers import PostSerializer

from .backends import search_posts, search_users
from .serializers import UserSearchSerializer

User = get_user_model()

PREVIEW_SIZE = 5  # per-type results shown on the "All" tab
MAX_LIMIT = 50


class SearchAPIView(APIView):
    """GET /search/?q=&type=all|users|posts&limit=&offset="""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.GET.get("q", "").strip()
        type_ = request.GET.get("type", "all")
        limit = self._int(request.GET.get("limit"), 10, MAX_LIMIT)
        offset = self._int(request.GET.get("offset"), 0, None)

        if not q:
            if type_ == "all":
                return Response(
                    {
                        "users": {"count": 0, "results": []},
                        "posts": {"count": 0, "results": []},
                    }
                )
            return Response({"count": 0, "results": [], "has_more": False})

        if type_ == "users":
            return Response(self._users(q, offset, limit))
        if type_ == "posts":
            return Response(self._posts(request, q, offset, limit))

        # "all" tab: a small preview of each type.
        return Response(
            {
                "users": self._users(q, 0, PREVIEW_SIZE),
                "posts": self._posts(request, q, 0, PREVIEW_SIZE),
            }
        )

    @staticmethod
    def _int(value, default, cap):
        try:
            n = int(value)
        except (TypeError, ValueError):
            return default
        n = max(n, 0)
        return min(n, cap) if cap is not None else n

    def _users(self, q, offset, limit):
        total, ids = search_users(q, offset, limit)
        by_id = {u.id: u for u in User.objects.filter(id__in=ids)}
        ordered = [by_id[i] for i in ids if i in by_id]
        results = UserSearchSerializer(ordered, many=True).data
        return {"count": total, "results": results, "has_more": offset + limit < total}

    def _posts(self, request, q, offset, limit):
        total, ids = search_posts(q, offset, limit)
        qs = Post.objects.select_related("author").filter(id__in=ids).annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
        if request.user.is_authenticated:
            qs = qs.annotate(
                liked_by_user=Exists(
                    Like.objects.filter(post=OuterRef("pk"), user=request.user)
                )
            )
        by_id = {p.id: p for p in qs}
        ordered = [by_id[i] for i in ids if i in by_id]
        results = PostSerializer(ordered, many=True, context={"request": request}).data
        return {"count": total, "results": results, "has_more": offset + limit < total}
