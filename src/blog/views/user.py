from typing import Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from blog.forms import (
    RestorePasswordForm,
    UserLoginForm,
    UserRegisterForm,
)
from config.settings import DOMAIN_NAME, EMAIL_SENDER


class UserLogin(SuccessMessageMixin, LoginView):
    template_name = "blog/login.html"
    redirect_field_name = "blog"
    redirect_authenticated_user = True
    authentication_form = UserLoginForm
    success_messages = "Вы успешно зарегистрировались"

    def get_success_message(self, cleaned_data) -> str:
        return self.success_messages

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"{DOMAIN_NAME} | Авторизация"
        context["logo_name"] = DOMAIN_NAME
        return context


class UserLogout(LogoutView):
    next_page = "home"


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались")
            return redirect("home")
        else:
            messages.error(request, "Ошибка регистрации")
    else:
        form = UserRegisterForm()
    context = {
        "form": form,
        "title": f"{DOMAIN_NAME} | Регистрация",
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/register.html", context=context)


def restore_password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            new_password = User.objects.make_random_password()
            user_email = form.cleaned_data["email"]
            current_user = User.objects.filter(email=user_email).first()
            if current_user:
                current_user.set_password(new_password)
                current_user.save()
            send_mail(
                subject="Восстановление пароля",
                message=f"Новый пароль {new_password}",
                from_email=EMAIL_SENDER,
                recipient_list=[form.cleaned_data["email"]],
            )
            return HttpResponse("Письмо с новым паролем было успешно отправлено")
    restore_password_form = RestorePasswordForm()
    context = {
        "form": restore_password_form,
        "title": f"{DOMAIN_NAME} | Восстановление пароля",
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/restore_password.html", context=context)


def get_profile(request: HttpRequest) -> HttpResponse:
    context = {
        "title": f"{DOMAIN_NAME} | Контакты",
        "logo_name": DOMAIN_NAME,
    }
    return render(request, "blog/profile.html", context=context)
