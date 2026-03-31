from typing import Protocol

from blog.exceptions import TagNotFoundError
from blog.models import Tag


class TagRepositoryProtocol(Protocol):
    def get_by_slug(self, slug: str) -> Tag: ...


class TagRepository:
    def get_by_slug(self, slug: str) -> Tag:
        try:
            return Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            raise TagNotFoundError(f"Tag with slug '{slug}' not found") from None
