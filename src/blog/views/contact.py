from datetime import datetime

from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

from blog.forms import (
    ContactForm,
)
from config.settings import DOMAIN_NAME, EMAIL_RECIPIENT, EMAIL_SENDER


def contact(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = f'[{DOMAIN_NAME}] {form.cleaned_data["subject"]}'
            recipient = form.cleaned_data["email"]
            now = datetime.now()

            html_message_sender = loader.render_to_string(
                "email/contact.html",
                {
                    "name": f'[{form.cleaned_data["name"]}] - {recipient}',
                    "logo": DOMAIN_NAME,
                    "message": form.cleaned_data["message"],
                    "year": now.year,
                },
            )
            mail_to_sender = send_mail(
                subject,
                "",
                EMAIL_SENDER,
                [
                    EMAIL_RECIPIENT,
                ],
                fail_silently=True,
                html_message=html_message_sender,
            )
            if mail_to_sender:
                messages.success(request, "Письмо отправлено")
                return redirect("contact")
            else:
                messages.error(request, "Ошибка отправки письма")
    else:
        form = ContactForm()
    context = {
        "form": form,
        "title": f"{DOMAIN_NAME} | Контакты",
        "email": EMAIL_RECIPIENT,
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/contact.html", context=context)
