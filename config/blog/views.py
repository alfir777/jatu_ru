from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from config.settings import DOMAIN_NAME
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


def index(request):
    return render(request, 'blog/index.html')


def portfolio(request):
    return render(request, 'blog/portfolio.html')


def contact(request):
    return render(request, 'blog/contact.html')


def test(request):
    return HttpResponse('<h1>TEST</h1>')


def get_category(request, slug):
    return render(request, 'blog/category.html')


def get_post(request, slug):
    return render(request, 'blog/post.html')
