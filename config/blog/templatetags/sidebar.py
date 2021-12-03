from django import template

from blog.models import Post, Tag

register = template.Library()


@register.inclusion_tag('blog/popular_posts_tpl.html')
def get_popular(cnt=3):
    posts = Post.objects.order_by('-views')[:cnt].select_related('category', 'author').prefetch_related('tags')
    return {'posts': posts}


@register.inclusion_tag('blog/tags_tpl.html')
def get_list_tags():
    tags = Tag.objects.all()
    return {'tags': tags}
