from django.db import models
from django.urls import reverse


class Category(models.Model):
    title = models.CharField(
        max_length=255, db_index=True, verbose_name="Название категории"
    )
    slug = models.SlugField(max_length=255, verbose_name="Url", unique=True)

    def get_absolute_url(self) -> str:
        return reverse("category", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]
