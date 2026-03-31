from typing import Protocol

from blog.exceptions import CategoryNotFoundError
from blog.models import Category


class CategoryRepositoryProtocol(Protocol):
    def get_by_slug(self, slug: str) -> Category: ...


class CategoryRepository:
    def get_by_slug(self, slug: str) -> Category:
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise CategoryNotFoundError(
                f"Category with slug '{slug}' not found"
            ) from None
