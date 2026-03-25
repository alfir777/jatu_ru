from typing import Any

from config.settings import DOMAIN_NAME


class LogoNameMixin:
    context_object_name = "posts"

    @staticmethod
    def get_user_context(**kwargs) -> dict[str, Any]:
        context = kwargs
        context["logo_name"] = DOMAIN_NAME
        return context
