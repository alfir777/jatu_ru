from django.contrib.auth.models import User
from django.core.mail import send_mail

from blog.exceptions import EmailSendError
from config.settings import EMAIL_SENDER


class UserService:
    def restore_password(self, email: str) -> None:
        new_password = User.objects.make_random_password()
        current_user = User.objects.filter(email=email).first()
        if current_user:
            current_user.set_password(new_password)
            current_user.save()
        result = send_mail(
            subject="Восстановление пароля",
            message=f"Новый пароль: {new_password}",
            from_email=EMAIL_SENDER,
            recipient_list=[email],
            fail_silently=False,
        )
        if not result:
            raise EmailSendError("Failed to send password reset email")
