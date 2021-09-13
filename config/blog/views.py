from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator

from config.settings import DOMAIN_NAME
from .models import Post, Category, Tag


class Blog(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = DOMAIN_NAME
        return context


class PostByCategory(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 2
    allow_empty = False

    def get_queryset(self):
        return Post.objects.filter(category__slug=self.kwargs['slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Category.objects.get(slug=self.kwargs['slug'])
        return context



def index(request):
    return render(request, 'blog/index.html')


def portfolio(request):
    return render(request, 'blog/portfolio.html')


def contact(request):
    return render(request, 'blog/contact.html')


def test(request):
    return HttpResponse('<h1>TEST</h1>')


def get_post(request, slug):
    return render(request, 'blog/post.html')
