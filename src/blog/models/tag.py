from django.db import models
from django.urls import reverse


class Tag(models.Model):
    title = models.CharField(max_length=50, db_index=True, verbose_name="Название тега")
    slug = models.SlugField(max_length=50, verbose_name="Url", unique=True)

    def get_absolute_url(self) -> str:
        return reverse("tag", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["title"]
