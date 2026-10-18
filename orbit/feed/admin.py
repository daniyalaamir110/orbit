from django.contrib import admin

from .models import Comment, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "content", "created")
    search_fields = ("content", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created")
