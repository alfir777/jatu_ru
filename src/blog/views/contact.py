from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from blog.container import contact_service
from blog.forms import ContactForm
from config.settings import DOMAIN_NAME, EMAIL_RECIPIENT


def contact(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            sent = contact_service.send_contact_email(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
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
        "form": form,
        "title": f"{DOMAIN_NAME} | Контакты",
        "email": EMAIL_RECIPIENT,
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/contact.html", context=context)
