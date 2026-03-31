from django.contrib.auth.models import User
from django.db.models import QuerySet
from pytils.translit import slugify

from blog.exceptions import DuplicatePostTitleError, UnauthorizedError
from blog.models import Category, Post
from blog.repositories.category import CategoryRepositoryProtocol
from blog.repositories.post import PostRepositoryProtocol
from blog.repositories.tag import TagRepositoryProtocol


class PostService:
    def __init__(
        self,
        post_repo: PostRepositoryProtocol,
        category_repo: CategoryRepositoryProtocol,
        tag_repo: TagRepositoryProtocol,
    ) -> None:
        self._post_repo = post_repo
        self._category_repo = category_repo
        self._tag_repo = tag_repo

    def get_published_posts(self) -> QuerySet[Post]:
        return self._post_repo.get_published()

    def get_post_by_slug(self, slug: str) -> Post:
        return self._post_repo.get_by_slug(slug)

    def get_posts_by_category(self, slug: str) -> QuerySet[Post]:
        return self._post_repo.get_by_category_slug(slug)

    def get_posts_by_tag(self, slug: str) -> QuerySet[Post]:
        return self._post_repo.get_by_tag_slug(slug)

    def get_category_title(self, slug: str) -> str:
        return str(self._category_repo.get_by_slug(slug))

    def get_tag_title(self, slug: str) -> str:
        return str(self._tag_repo.get_by_slug(slug))

    def create_post(
        self,
        user: User,
        title: str,
        description: str,
        content: str,
        is_published: bool,
        category: Category,
        tags: list,
    ) -> Post:
        if not user.is_staff:
            raise UnauthorizedError("Only staff can create posts")
        if self._post_repo.slug_exists(slugify(title)):
            raise DuplicatePostTitleError("Post title must be unique")
        post = self._post_repo.create(
            title=title,
            author=user,
            description=description,
            content=content,
            is_published=is_published,
            category=category,
        )
        if tags:
            post.tags.set(tags)
        return post

    def update_post(
        self,
        slug: str,
        user: User,
        title: str,
        description: str,
        content: str,
        is_published: bool,
        category: Category,
        tags: list,
    ) -> Post:
        post = self._post_repo.get_by_slug(slug)
        if not user.is_staff:
            raise UnauthorizedError("Only staff can update posts")
        if post.author != user:
            raise UnauthorizedError("Only the author can edit this post")
        post = self._post_repo.update(
            post,
            title=title,
            description=description,
            content=content,
            is_published=is_published,
            category=category,
        )
        post.tags.set(tags)
        return post

    def delete_post(self, slug: str, user: User) -> None:
        post = self._post_repo.get_by_slug(slug)
        if post.author != user:
            raise UnauthorizedError("Only the author can delete this post")
        self._post_repo.delete(post)

    def increment_views(self, pk: int) -> None:
        self._post_repo.increment_views(pk)

    def search_posts(self, query: str) -> QuerySet[Post]:
        return self._post_repo.search(query)
