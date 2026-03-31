from typing import Any

from django.db.models import QuerySet
from django.views.generic import ListView

from blog.container import post_service
from blog.mixins import LogoNameMixin
from blog.models import Post
from config.settings import DOMAIN_NAME


class Search(LogoNameMixin, ListView):
    template_name = "blog/search.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Post]:
        return post_service.search_posts(self.request.GET.get("s", ""))

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["s"] = f"s={self.request.GET.get('s', '')}&"
        context.update(self.get_user_context(title=f"{DOMAIN_NAME} | Поиск"))
        return context
