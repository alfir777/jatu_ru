from config.settings import DOMAIN_NAME


class DataMixin:
    context_object_name = 'posts'

    def get_user_context(self, **kwargs):
        context = kwargs
        context['logo_name'] = DOMAIN_NAME
        return context
