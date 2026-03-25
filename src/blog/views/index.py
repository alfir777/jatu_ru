from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from blog.forms import (
    ContactForm,
)
from config.settings import DOMAIN_NAME, EMAIL_RECIPIENT, EMAIL_SENDER


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(
                form.cleaned_data["subject"],
                form.cleaned_data["message"],
                EMAIL_SENDER,
                [EMAIL_RECIPIENT],
                fail_silently=True,
            )
            if mail:
                messages.success(request, "Письмо отправлено")
                return redirect("contact")
            else:
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
