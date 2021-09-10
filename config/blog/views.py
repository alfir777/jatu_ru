from django.shortcuts import render
from django.http import HttpResponse

from .models import Post, Category


def index(request):
    return render(request, 'blog/index.html')


def portfolio(request):
    return render(request, 'blog/portfolio.html')


def blog(request):
    return render(request, 'blog/blog.html')


def contact(request):
    return render(request, 'blog/contact.html')


def test(request):
    return HttpResponse('<h1>TEST</h1>')


def get_category(request, slug):
    # blogs = Post.objects.filter(category_id=category_id)
    # category = Category.objects.get(pk=category_id)
    # return render(request, 'blog/category.html', {'blogs': blogs, 'category': category})
    return render(request, 'blog/category.html')
