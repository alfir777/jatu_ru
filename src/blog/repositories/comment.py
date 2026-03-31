from typing import Protocol

from django.contrib.auth.models import User
from django.db.models import QuerySet

from blog.models import Comment, Post


class CommentRepositoryProtocol(Protocol):
    def get_for_post(self, post: Post) -> QuerySet[Comment]: ...
    def create(self, post: Post, author: User, content: str) -> Comment: ...


class CommentRepository:
    def get_for_post(self, post: Post) -> QuerySet[Comment]:
        return (
            Comment.objects.filter(post=post, is_published=True)
            .order_by("created_at")
            .select_related("post", "author", "parent")
        )

    def create(self, post: Post, author: User, content: str) -> Comment:
        return Comment.objects.create(post=post, author=author, content=content)
