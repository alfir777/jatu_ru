from django.contrib import messages
from django.contrib.auth import login, get_user
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


class Blog(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = DOMAIN_NAME
        return context


class PostByCategory(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(category__slug=self.kwargs['slug'], is_published=True).select_related('category')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(Category.objects.get(slug=self.kwargs['slug']))
        return context


class PostByTag(ListView):
    template_name = 'blog/tags.html'
    context_object_name = 'posts'
    paginate_by = 10
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs['slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Tag.objects.get(slug=self.kwargs['slug'])
        return context


class GetPost(DetailView):
    model = Post
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()
        comment_list = (
            Comment.objects.filter(post=self.object).order_by('created_at')
        )
        comment_count = Comment.objects.filter(post=self.object).order_by('created_at').count()
        context['comment_count'] = comment_count
        context['comments'] = comment_list
        for comment in comment_list:
            comment._post_url = self.object.get_absolute_url()
        context['form'] = UserCommentForm(initial={'post': self.object.slug})
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


class Search(ListView):
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(title__icontains=self.request.GET.get('s'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s'] = f"s={self.request.GET.get('s')}&"
        return context


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
    return render(request, 'blog/register.html', {'form': form})


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
        'form': restore_password_form
    }
    return render(request, 'blog/restore_password.html', context=context)


class UserLogin(SuccessMessageMixin, LoginView):
    template_name = 'blog/login.html'
    redirect_field_name = 'home'
    redirect_authenticated_user = True
    authentication_form = UserLoginForm
    success_messages = 'Вы успешно зарегистрировались'

    def get_success_message(self, cleaned_data):
        return self.success_messages


class UserLogout(LogoutView):
    next_page = 'home'


def blog_add_post(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = get_user(request)
            post = Post.objects.create(**form.cleaned_data)
            return redirect(post)
    else:
        form = BlogForm()
    return render(request, 'blog/blog_add_post.html', {'form': form})


def index(request):
    return render(request, 'blog/index.html')


def portfolio(request):
    return render(request, 'blog/portfolio.html')


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
    return render(request, 'blog/contact.html', {'form': form})


def test(request):
    return HttpResponse('<h1>TEST</h1>')


class RobotsTxtView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'
