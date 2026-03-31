from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from blog.container import contact_service
from blog.forms import ContactForm
from config.settings import DOMAIN_NAME


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            sent = contact_service.send_simple_email(
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
            )
            if sent:
                messages.success(request, "Письмо отправлено")
                return redirect("contact")
            messages.error(request, "Ошибка отправки письма")
    else:
        form = ContactForm()
    context = {
        "title": f"{DOMAIN_NAME} | Добро пожаловать",
        "form": form,
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/index.html", context=context)


class RobotsTxtView(TemplateView):
    template_name = "robots.txt"
    content_type = "text/plain"
