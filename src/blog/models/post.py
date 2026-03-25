from typing import Any

from django.db import models
from django.urls import reverse
from pytils.translit import slugify


class Post(models.Model):
    title = models.CharField(max_length=255, db_index=True, verbose_name="Заголовок")
    description = models.TextField(max_length=255, verbose_name="Описание", default="")
    slug = models.SlugField(
        max_length=255, db_index=True, verbose_name="Url", unique=True
    )
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    photo = models.ImageField(
        upload_to="photos/%Y/%m/%d/", blank=True, verbose_name="Фото"
    )
    views = models.IntegerField(default=0, verbose_name="Количество просмотров")
    category = models.ForeignKey(
        "blog.Category",
        on_delete=models.PROTECT,
        related_name="posts",
        verbose_name="Категория",
    )
    tags = models.ManyToManyField("blog.Tag", blank=True, related_name="posts")
    votes = models.IntegerField(default=0, verbose_name="Количество голосов")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("post", kwargs={"slug": self.slug})

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-created_at"]
