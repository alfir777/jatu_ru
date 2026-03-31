from datetime import datetime

from django.core.mail import send_mail
from django.template import loader

from config.settings import DOMAIN_NAME, EMAIL_RECIPIENT, EMAIL_SENDER


class ContactService:
    def send_contact_email(
        self, name: str, email: str, subject: str, message: str
    ) -> bool:
        full_subject = f"[{DOMAIN_NAME}] {subject}"
        now = datetime.now()
        html_message = loader.render_to_string(
            "email/contact.html",
            {
                "name": f"[{name}] - {email}",
                "logo": DOMAIN_NAME,
                "message": message,
                "year": now.year,
            },
        )
        return bool(
            send_mail(
                full_subject,
                "",
                EMAIL_SENDER,
                [EMAIL_RECIPIENT],
                fail_silently=True,
                html_message=html_message,
            )
        )

    def send_simple_email(self, subject: str, message: str) -> bool:
        return bool(
            send_mail(
                subject,
                message,
                EMAIL_SENDER,
                [EMAIL_RECIPIENT],
                fail_silently=True,
            )
        )
