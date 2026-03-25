from typing import Any

from django import template
from django.db.models import Count, F

from blog.models import Category

register = template.Library()


@register.inclusion_tag("blog/menu_tpl.html")
def show_menu(menu_class: str = "menu") -> dict[str, Any]:
    categories = Category.objects.all()
    return {"categories": categories, "menu_class": menu_class}


@register.inclusion_tag("blog/menu_tpl.html")
def show_categories() -> dict[str, Any]:
    categories = Category.objects.annotate(
        cnt=Count("post", filter=F("post__is_published"))
    ).filter(cnt__gt=0)
    return {"categories": categories}
