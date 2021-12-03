from django.contrib import messages
from django.contrib.auth import login, get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView

from config.settings import DOMAIN_NAME, EMAIL_SENDER, EMAIL_RECIPIEN
from .forms import *
from .models import Post, Category, Tag, Comment
from .utils import DataMixin


class Blog(DataMixin, ListView):
    model = Post
    template_name = 'blog/blog.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f'{DOMAIN_NAME} | Блог')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related('tags')


class PostByCategory(DataMixin, ListView):
    template_name = 'blog/category.html'
    paginate_by = 10
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(
            category__slug=self.kwargs['slug'],
            is_published=True
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f'{DOMAIN_NAME} | {str(Category.objects.get(slug=self.kwargs["slug"]))}')
        return dict(list(context.items()) + list(c_def.items()))


class PostByTag(DataMixin, ListView):
    template_name = 'blog/tags.html'
    paginate_by = 10
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(
            tags__slug=self.kwargs['slug'], is_published=True
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f'{DOMAIN_NAME} | {Tag.objects.get(slug=self.kwargs["slug"])}')
        return dict(list(context.items()) + list(c_def.items()))


class GetPost(DetailView):
    model = Post
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()
        comments = (
            Comment.objects.filter(
                post=self.object).order_by('created_at').select_related('post', 'author', 'parent')
        )
        context['comment_count'] = comments.count()
        context['comments'] = comments
        for comment in comments:
            comment._post_url = self.object.get_absolute_url()
        context['form'] = UserCommentForm(initial={'post': self.object.slug})
        context['description'] = self.object.description
        context['title'] = f'{DOMAIN_NAME} | {self.object.title}'
        context['logo_name'] = DOMAIN_NAME
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated:
            form = UserCommentForm(request.POST)
        else:
            form = GuestCommentForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = get_user(request)
            form.cleaned_data['post_id'] = self.object.pk
            comment = Comment.objects.create(**form.cleaned_data)
            form.save(request=request, obj=comment, form=form)
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
            return redirect(self.object)
        else:
            messages.add_message(request, messages.WARNING, 'Нет прав на добавления комментария')
            return redirect(self.object)


class Search(DataMixin, ListView):
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            title__icontains=self.request.GET.get('s')
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s'] = f"s={self.request.GET.get('s')}&"
        c_def = self.get_user_context(title=f'{DOMAIN_NAME} | Поиск')
        return dict(list(context.items()) + list(c_def.items()))


class UserLogin(SuccessMessageMixin, LoginView):
    template_name = 'blog/login.html'
    redirect_field_name = 'blog'
    redirect_authenticated_user = True
    authentication_form = UserLoginForm
    success_messages = 'Вы успешно зарегистрировались'

    def get_success_message(self, cleaned_data):
        return self.success_messages

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{DOMAIN_NAME} | Авторизация'
        context['logo_name'] = DOMAIN_NAME
        return context


class UserLogout(LogoutView):
    next_page = 'home'


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
        'title': f'{DOMAIN_NAME} | Регистрация',
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/register.html', context=context)


def restore_password(request):
    if request.method == 'POST':
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            new_password = User.objects.make_random_password()
            user_email = form.cleaned_data['email']
            current_user = User.objects.filter(email=user_email).first()
            if current_user:
                current_user.set_password(new_password)
                current_user.save()
            send_mail(
                subject='Восстановление пароля',
                message=f'Новый пароль {new_password}',
                from_email=EMAIL_SENDER,
                recipient_list=[form.cleaned_data['email']],
            )
            return HttpResponse('Письмо с новым паролем было успешно отправлено')
    restore_password_form = RestorePasswordForm()
    context = {
        'form': restore_password_form,
        'title': f'{DOMAIN_NAME} | Восстановление пароля',
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/restore_password.html', context=context)


@login_required(redirect_field_name='blog', login_url='user_login')
def blog_add_post(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = get_user(request)
            post = Post.objects.create(**form.cleaned_data)
            return redirect(post)
    else:
        form = BlogForm()
    context = {
        'form': form,
        'title': f'{DOMAIN_NAME} | Добавление поста',
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/blog_add_post.html', context=context)


def index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'],
                             form.cleaned_data['content'],
                             EMAIL_SENDER,
                             [EMAIL_RECIPIEN],
                             fail_silently=True
                             )
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('contact')
            else:
                messages.error(request, 'Ошибка отправки письма')
    else:
        form = ContactForm()
    context = {
        'title': f'{DOMAIN_NAME} | Добро пожаловать',
        'form': form,
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/index.html', context=context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'],
                             form.cleaned_data['content'],
                             EMAIL_SENDER,
                             [EMAIL_RECIPIEN],
                             fail_silently=True
                             )
            if mail:
                messages.success(request, 'Письмо отправлено')
                return redirect('contact')
            else:
                messages.error(request, 'Ошибка отправки письма')
    else:
        form = ContactForm()
    context = {
        'form': form,
        'title': f'{DOMAIN_NAME} | Контакты',
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/contact.html', context=context)


class RobotsTxtView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'


def get_profile(request):
    context = {
        'title': f'{DOMAIN_NAME} | Контакты',
        'logo_name': DOMAIN_NAME,
    }
    return render(request, 'blog/profile.html', context=context)


def page_not_found(request, exception, template_name='blog/404.html'):
    return render(request, 'blog/404.html')
