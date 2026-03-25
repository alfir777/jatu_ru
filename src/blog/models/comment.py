from django.db import models


class Comment(models.Model):
    post = models.ForeignKey(
        "blog.Post", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    votes = models.IntegerField(default=0, verbose_name="Количество голосов")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    def __str__(self) -> str:
        return f'Comment by "{self.author}" on "{self.post}"'

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]
