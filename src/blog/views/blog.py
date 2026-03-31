from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from blog.container import comment_service, post_service
from blog.exceptions import DuplicatePostTitleError, UnauthorizedError
from blog.forms import BlogForm, UserCommentForm
from blog.mixins import LogoNameMixin
from blog.models import Post
from config.settings import DOMAIN_NAME


class BlogListView(LogoNameMixin, ListView):
    model = Post
    template_name = "blog/blog.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Post]:
        return post_service.get_published_posts()

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_context(title=f"{DOMAIN_NAME} | Блог"))
        return context


class BlogByCategory(LogoNameMixin, ListView):
    template_name = "blog/category.html"
    paginate_by = 10
    allow_empty = False

    def get_queryset(self) -> QuerySet[Post]:
        return post_service.get_posts_by_category(self.kwargs["slug"])

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        category_title = post_service.get_category_title(self.kwargs["slug"])
        context.update(self.get_user_context(title=f"{DOMAIN_NAME} | {category_title}"))
        return context


class BlogByTag(LogoNameMixin, ListView):
    template_name = "blog/tags.html"
    paginate_by = 10
    allow_empty = False

    def get_queryset(self) -> QuerySet[Post]:
        return post_service.get_posts_by_tag(self.kwargs["slug"])

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tag_title = post_service.get_tag_title(self.kwargs["slug"])
        context.update(self.get_user_context(title=f"{DOMAIN_NAME} | {tag_title}"))
        return context


class BlogDetailView(DetailView):
    model = Post
    template_name = "blog/blog_detail.html"
    context_object_name = "post"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)
        post_service.increment_views(self.object.pk)
        return response

    def get_context_data(self, *, object_list=None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        comments = comment_service.get_comments_for_post(self.object)
        context["comment_count"] = comments.count()
        context["comments"] = comments
        context["form"] = UserCommentForm()
        context["description"] = self.object.description
        context["title"] = f"{DOMAIN_NAME} | {self.object.title}"
        context["logo_name"] = DOMAIN_NAME
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        post = post_service.get_post_by_slug(self.kwargs["slug"])
        if not request.user.is_authenticated:
            messages.warning(request, "Нет прав на добавление комментария")
            return redirect(post)
        form = UserCommentForm(request.POST)
        if form.is_valid():
            comment_service.add_comment(
                post=post,
                author=request.user,
                content=form.cleaned_data["content"],
            )
            messages.success(request, "Комментарий добавлен (на модерации)")
            return redirect(post)
        messages.warning(request, "Ошибка при добавлении комментария")
        return redirect(post)


class BlogCreateView(LoginRequiredMixin, CreateView):
    form_class = BlogForm
    template_name = "blog/blog_post_add.html"
    login_url = "/login/"
    redirect_field_name = "/blog/"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"{DOMAIN_NAME} | Добавление поста"
        context["logo_name"] = DOMAIN_NAME
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BlogForm(request.POST)
        if form.is_valid():
            try:
                post = post_service.create_post(
                    user=request.user,
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    content=form.cleaned_data["content"],
                    is_published=form.cleaned_data["is_published"],
                    category=form.cleaned_data["category"],
                    tags=request.POST.getlist("tags"),
                )
                return redirect(post)
            except UnauthorizedError:
                messages.warning(request, "Нет прав на добавление поста")
            except DuplicatePostTitleError:
                messages.error(request, "Название поста должно быть уникальным")
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

    def get_object(self, *args: Any, **kwargs: Any) -> Post:
        return post_service.get_post_by_slug(self.kwargs["slug"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"{DOMAIN_NAME} | Редактирование поста"
        context["logo_name"] = DOMAIN_NAME
        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BlogForm(request.POST)
        if form.is_valid():
            try:
                post = post_service.update_post(
                    slug=self.kwargs["slug"],
                    user=request.user,
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    content=form.cleaned_data["content"],
                    is_published=form.cleaned_data["is_published"],
                    category=form.cleaned_data["category"],
                    tags=request.POST.getlist("tags"),
                )
                return redirect(post)
            except UnauthorizedError as exc:
                messages.warning(request, str(exc))
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

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        if post.author != request.user:
            messages.error(
                request, "Пост может удалить только автор поста или администратор"
            )
            return redirect(self.success_url)
        return render(request, "blog/blog_post_delete.html", {"title": post.title})

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            post_service.delete_post(slug=self.kwargs["slug"], user=request.user)
            messages.success(request, "Пост был успешно удален.")
        except UnauthorizedError as exc:
            messages.error(request, str(exc))
        return redirect(self.success_url)
