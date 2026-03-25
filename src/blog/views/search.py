from typing import Any

from django.db.models import QuerySet
from django.views.generic import ListView

from blog.mixins import LogoNameMixin
from blog.models import Post
from config.settings import DOMAIN_NAME


class Search(LogoNameMixin, ListView):
    template_name = "blog/search.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.filter(title__icontains=self.request.GET.get("s"))
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["s"] = f"s={self.request.GET.get('s')}&"
        c_def = self.get_user_context(title=f"{DOMAIN_NAME} | Поиск")
        return dict(list(context.items()) + list(c_def.items()))
