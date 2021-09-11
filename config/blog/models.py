from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

"""
Category
==================
title, slug

Tag
==================
title, slug

Post
==================
title, slug, author, content, created_at, updated_at, photo, views, category, tags, votes, is_published

Comment
==================
post, author, body, created_at, updated_at, votes, is_published

"""


class Category(models.Model):
    title = models.CharField(max_length=255, db_index=True, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Tag(models.Model):
    title = models.CharField(max_length=50, db_index=True, verbose_name='Название тега')
    slug = models.SlugField(max_length=50, verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['title']


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='posts')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    photo = models.ImageField(upload_to='photos/%Y/%M/%d/', blank=True, verbose_name='Фото')
    views = models.IntegerField(default=0, verbose_name='Количество просмотров')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts', verbose_name='Категория')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    votes = models.IntegerField(default=0, verbose_name='Количество голосов')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']


class Comment(models.Model):
    slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comments')
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    votes = models.IntegerField(default=0, verbose_name='Количество голосов')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author, self.post)

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ['-created_at']