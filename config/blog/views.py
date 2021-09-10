from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'blog/index.html')


def test(request):
    return HttpResponse('<h1>TEST</h1>')
