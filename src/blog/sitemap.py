from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from blog.models import Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self) -> QuerySet[Post]:
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj: Post) -> datetime:
        return obj.updated_at
