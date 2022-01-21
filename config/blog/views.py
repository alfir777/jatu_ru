import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from config.settings import DOMAIN_NAME, EMAIL_SENDER, EMAIL_RECIPIEN
from .forms import *
from .models import Post, Category, Tag, Comment
from .utils import DataMixin


class BlogListView(DataMixin, ListView):
    model = Post
    template_name = 'blog/blog.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f'{DOMAIN_NAME} | Блог')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related('tags')


class BlogByCategory(DataMixin, ListView):
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


class BlogByTag(DataMixin, ListView):
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


class BlogDetailView(DetailView):
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
        post = self.get_object()
        if request.user.is_authenticated:
            form = UserCommentForm(request.POST)
        else:
            form = GuestCommentForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = get_user(request)
            form.cleaned_data['post_id'] = post.pk
            comment = Comment.objects.create(**form.cleaned_data)
            form.save(request=request, obj=comment, form=form)
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
            return redirect(post)
        else:
            messages.add_message(request, messages.WARNING, 'Нет прав на добавления комментария')
            return redirect(self.object)


class BlogCreateView(LoginRequiredMixin, CreateView):
    form_class = BlogForm
    template_name = 'blog/blog_post_add.html'
    login_url = '/login/'
    redirect_field_name = '/blog/'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = BlogForm(request.POST)
            if form.is_valid():
                if len(Post.objects.filter(slug=slugify(form.cleaned_data['title']))) == 1:
                    messages.error(request, 'Название поста должно быть уникальным')
                    context = {
                        'form': form,
                        'title': f'{DOMAIN_NAME} | Добавление поста',
                        'logo_name': DOMAIN_NAME,
                    }
                    return render(request, 'blog/blog_post_add.html', context=context)
                else:
                    post = Post(title=form.cleaned_data['title'],
                                author=request.user,
                                description=form.cleaned_data['description'],
                                )
                    post.content = form.cleaned_data['content']
                    post.is_published = form.cleaned_data['is_published']
                    post.category = form.cleaned_data['category']
                    if request.POST.getlist('tags'):
                        post.tags.set(*request.POST.getlist('tags'))
                    post.save()
                    return redirect(post)
        else:
            form = BlogForm()
        context = {
            'form': form,
            'title': f'{DOMAIN_NAME} | Добавление поста',
            'logo_name': DOMAIN_NAME,
        }
        return render(request, 'blog/blog_post_add.html', context=context)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    Model = Post
    form_class = BlogForm
    template_name = 'blog/blog_post_edit.html'
    login_url = '/login/'
    redirect_field_name = '/blog/'

    def get_object(self, *args, **kwargs):
        return Post.objects.get(slug=self.kwargs['slug'])

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = BlogForm(request.POST)
            if form.is_valid():
                post = Post.objects.get(slug=self.kwargs['slug'])
                if get_user(request) != post.author:
                    messages.error(request, 'Изменить пост имеет право только автор поста')
                    return redirect(post)
                else:
                    post.title = form.cleaned_data['title']
                    post.description = form.cleaned_data['description']
                    post.content = form.cleaned_data['content']
                    post.is_published = form.cleaned_data['is_published']
                    post.category = form.cleaned_data['category']
                    post.tags.set(*request.POST.getlist('tags'))
                    post.save()
                    return redirect(post)
        else:
            form = BlogForm()
        context = {
            'form': form,
            'title': f'{DOMAIN_NAME} | Добавление поста',
            'logo_name': DOMAIN_NAME,
        }
        return render(request, 'blog/blog_post_edit.html', context=context)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/blog_post_delete.html'
    success_url = reverse_lazy('blog')
    success_message = "Пост был успешно удален."

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            messages.error(request, 'Пост может удалить только автор поста или администратор')
            return redirect(self.success_url)
        return render(request, 'blog/blog_post_delete.html', {'title': post.title})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BlogDeleteView, self).delete(request, *args, **kwargs)


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
            subject = f'[{os.environ["DOMAIN_NAME"]}] {form.cleaned_data["subject"]}'
            copy = form.cleaned_data['copy']
            recipient = form.cleaned_data["email"]
            now = datetime.now()

            if copy:
                message = 'Спасибо за отзыв! Ваше сообщение: ' + form.cleaned_data["message"]
            else:
                message = 'Спасибо за отзыв!'

            html_message_recipient = loader.render_to_string(
                'email/contact.html',
                {
                    'name': f'Привет, {form.cleaned_data["name"]}!',
                    'logo': DOMAIN_NAME,
                    'message': message,
                    'year': now.year,
                }
            )
            html_message_sender = loader.render_to_string(
                'email/contact.html',
                {
                    'name': f'[{form.cleaned_data["name"]}] - {recipient}',
                    'logo': DOMAIN_NAME,
                    'message': form.cleaned_data["message"],
                    'year': now.year,
                }
            )
            mail_to_sender = send_mail(subject,
                                       '',
                                       EMAIL_SENDER,
                                       [EMAIL_RECIPIEN, ],
                                       fail_silently=True,
                                       html_message=html_message_sender,
                                       )
            mail_to_recipient = send_mail(subject,
                                          '',
                                          EMAIL_SENDER,
                                          [recipient, ],
                                          fail_silently=True,
                                          html_message=html_message_recipient,
                                          )
            if mail_to_sender and mail_to_recipient:
                messages.success(request, 'Письмо отправлено')
                return redirect('contact')
            else:
                messages.error(request, 'Ошибка отправки письма')
    else:
        form = ContactForm()
    context = {
        'form': form,
        'title': f'{DOMAIN_NAME} | Контакты',
        'email': EMAIL_RECIPIEN,
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
