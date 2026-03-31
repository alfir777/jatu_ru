from typing import Protocol

from django.db.models import F, QuerySet

from blog.exceptions import PostNotFoundError
from blog.models import Post


class PostRepositoryProtocol(Protocol):
    def get_published(self) -> QuerySet[Post]: ...
    def get_by_slug(self, slug: str) -> Post: ...
    def get_by_category_slug(self, slug: str) -> QuerySet[Post]: ...
    def get_by_tag_slug(self, slug: str) -> QuerySet[Post]: ...
    def create(self, **kwargs: object) -> Post: ...
    def update(self, post: Post, **kwargs: object) -> Post: ...
    def delete(self, post: Post) -> None: ...
    def increment_views(self, pk: int) -> None: ...
    def search(self, query: str) -> QuerySet[Post]: ...
    def slug_exists(self, slug: str) -> bool: ...


class PostRepository:
    def get_published(self) -> QuerySet[Post]:
        return (
            Post.objects.filter(is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_by_slug(self, slug: str) -> Post:
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise PostNotFoundError(f"Post with slug '{slug}' not found") from None

    def get_by_category_slug(self, slug: str) -> QuerySet[Post]:
        return (
            Post.objects.filter(category__slug=slug, is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_by_tag_slug(self, slug: str) -> QuerySet[Post]:
        return (
            Post.objects.filter(tags__slug=slug, is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def create(self, **kwargs: object) -> Post:
        post = Post(**kwargs)
        post.save()
        return post

    def update(self, post: Post, **kwargs: object) -> Post:
        for key, value in kwargs.items():
            setattr(post, key, value)
        post.save()
        return post

    def delete(self, post: Post) -> None:
        post.delete()

    def increment_views(self, pk: int) -> None:
        Post.objects.filter(pk=pk).update(views=F("views") + 1)

    def search(self, query: str) -> QuerySet[Post]:
        return (
            Post.objects.filter(title__icontains=query)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def slug_exists(self, slug: str) -> bool:
        return Post.objects.filter(slug=slug).exists()
