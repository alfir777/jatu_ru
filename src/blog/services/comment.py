from django.contrib.auth.models import User
from django.db.models import QuerySet

from blog.models import Comment, Post
from blog.repositories.comment import CommentRepositoryProtocol


class CommentService:
    def __init__(self, comment_repo: CommentRepositoryProtocol) -> None:
        self._repo = comment_repo

    def get_comments_for_post(self, post: Post) -> QuerySet[Comment]:
        return self._repo.get_for_post(post)

    def add_comment(self, post: Post, author: User, content: str) -> Comment:
        return self._repo.create(post=post, author=author, content=content)
