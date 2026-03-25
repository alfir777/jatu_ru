from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from blog.forms import (
    BlogForm,
    GuestCommentForm,
    UserCommentForm,
)
from blog.mixins import LogoNameMixin
from blog.models import Category, Comment, Post, Tag
from config.settings import DOMAIN_NAME


class BlogListView(LogoNameMixin, ListView):
    model = Post
    template_name = "blog/blog.html"
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_context(title=f"{DOMAIN_NAME} | Блог"))
        return context

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.filter(is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )


class BlogByCategory(LogoNameMixin, ListView):
    template_name = "blog/category.html"
    paginate_by = 10
    allow_empty = False

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.filter(category__slug=self.kwargs["slug"], is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_context_data(self, *, object_list=None, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update(
            self.get_user_context(
                title=f'{DOMAIN_NAME} | {str(Category.objects.get(slug=self.kwargs["slug"]))}'
            )
        )
        return context


class BlogByTag(LogoNameMixin, ListView):
    template_name = "blog/tags.html"
    paginate_by = 10
    allow_empty = False

    def get_queryset(self) -> QuerySet[Post]:
        return (
            Post.objects.filter(tags__slug=self.kwargs["slug"], is_published=True)
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_context_data(self, *, object_list=None, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update(
            self.get_user_context(
                title=f'{DOMAIN_NAME} | {Tag.objects.get(slug=self.kwargs["slug"])}'
            )
        )
        return context


class BlogDetailView(DetailView):
    model = Post
    template_name = "blog/blog_detail.html"
    context_object_name = "post"

    def get(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)
        Post.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        self.object.refresh_from_db(fields=["views"])
        return response

    def get_context_data(self, *, object_list=None, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        comments = (
            Comment.objects.filter(post=self.object, is_published=True)
            .order_by("created_at")
            .select_related("post", "author", "parent")
        )
        context["comment_count"] = comments.count()
        context["comments"] = comments
        for comment in comments:
            comment._post_url = self.object.get_absolute_url()
        context["form"] = UserCommentForm(initial={"post": self.object.slug})
        context["description"] = self.object.description
        context["title"] = f"{DOMAIN_NAME} | {self.object.title}"
        context["logo_name"] = DOMAIN_NAME
        return context

    def post(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        if request.user.is_authenticated:
            form = UserCommentForm(request.POST)
        else:
            form = GuestCommentForm(request.POST)
        if form.is_valid():
            form.cleaned_data["author"] = get_user(request)
            form.cleaned_data["post_id"] = post.pk
            Comment.objects.create(**form.cleaned_data)
            messages.add_message(
                request, messages.SUCCESS, "Комментарий добавлен (на модерации)"
            )
            return redirect(post)
        else:
            messages.add_message(
                request, messages.WARNING, "Нет прав на добавления комментария"
            )
            return redirect(self.object)


class BlogCreateView(LoginRequiredMixin, CreateView):
    form_class = BlogForm
    template_name = "blog/blog_post_add.html"
    login_url = "/login/"
    redirect_field_name = "/blog/"

    def post(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        form = BlogForm(request.POST)
        if form.is_valid() and request.user.is_staff:
            if Post.objects.filter(slug=slugify(form.cleaned_data["title"])).exists():
                messages.error(request, "Название поста должно быть уникальным")
                context = {
                    "form": form,
                    "title": f"{DOMAIN_NAME} | Добавление поста",
                    "logo_name": DOMAIN_NAME,
                }
                return render(request, "blog/blog_post_add.html", context=context)
            post = Post(
                title=form.cleaned_data["title"],
                author=request.user,
                description=form.cleaned_data["description"],
            )
            post.content = form.cleaned_data["content"]
            post.is_published = form.cleaned_data["is_published"]
            post.category = form.cleaned_data["category"]
            post.save()
            tags = request.POST.getlist("tags")
            if tags:
                post.tags.set(tags)
            return redirect(post)
        elif form.is_valid() and not request.user.is_staff:
            messages.add_message(
                request, messages.WARNING, "Нет прав на добавление поста"
            )
        context = {
            "form": form,
            "title": f"{DOMAIN_NAME} | Добавление поста",
            "logo_name": DOMAIN_NAME,
        }
        return render(request, "blog/blog_post_add.html", context=context)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = BlogForm
    template_name = "blog/blog_post_edit.html"
    login_url = "/login/"
    redirect_field_name = "/blog/"

    def get_object(self, *args, **kwargs) -> Post:
        return Post.objects.get(slug=self.kwargs["slug"])

    def post(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        form = BlogForm(request.POST)
        if form.is_valid() and request.user.is_staff:
            post = Post.objects.get(slug=self.kwargs["slug"])
            if get_user(request) != post.author:
                messages.error(request, "Изменить пост имеет право только автор поста")
                return redirect(post)
            post.title = form.cleaned_data["title"]
            post.description = form.cleaned_data["description"]
            post.content = form.cleaned_data["content"]
            post.is_published = form.cleaned_data["is_published"]
            post.category = form.cleaned_data["category"]
            tags = request.POST.getlist("tags")
            post.tags.set(tags)
            post.save()
            return redirect(post)
        elif form.is_valid() and not request.user.is_staff:
            messages.add_message(
                request, messages.WARNING, "Нет прав на изменение поста"
            )
        context = {
            "form": form,
            "title": f"{DOMAIN_NAME} | Редактирование поста",
            "logo_name": DOMAIN_NAME,
        }
        return render(request, "blog/blog_post_edit.html", context=context)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/blog_post_delete.html"
    success_url = reverse_lazy("blog")
    success_message = "Пост был успешно удален."

    def get(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        if post.author != self.request.user:
            messages.error(
                request, "Пост может удалить только автор поста или администратор"
            )
            return redirect(self.success_url)
        return render(request, "blog/blog_post_delete.html", {"title": post.title})

    def delete(self, request: HttpRequest, *args, **kwargs: Any) -> HttpResponse:
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
