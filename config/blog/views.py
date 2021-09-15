from django.contrib import messages
from django.contrib.auth import logout, login, get_user
from django.core.mail import send_mail
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from config.settings import DOMAIN_NAME, EMAIL_SENDER, EMAIL_RECIPIEN
from .forms import UserRegisterForm, UserLoginForm, ContactForm, BlogForm
from .models import Post, Category, Tag


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
        return context


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


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'blog/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('user_login')


def blog_add_post(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            form.cleaned_data['author'] = get_user(request)
            post = Post.objects.create(**form.cleaned_data)
            return redirect(post)
        print(form)
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
