from config.settings import DOMAIN_NAME


class DataMixin:
    context_object_name = 'posts'

    @staticmethod
    def get_user_context(**kwargs):
        context = kwargs
        context['logo_name'] = DOMAIN_NAME
        return context
