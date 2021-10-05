from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.urls import reverse
from .models import Post


class LatestPostsFeed(Feed):
    title = 'RRS-лента'
    link = '/blog/'
    description = 'Самые свежие посты'

    def items(self) -> QuerySet:
        return Post.objects.filter(is_published=True).order_by('-created_at')[:10]

    def item_title(self, item: Post) -> str:
        return item.title

    def item_description(self, item: Post) -> str:
        return item.description

    def item_link(self, item: Post) -> str:
        return reverse('post', kwargs={'slug': item.slug})
