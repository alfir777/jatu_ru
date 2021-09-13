from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('portfolio/', portfolio, name='portfolio'),
    path('blog/', Blog.as_view(), name='blog'),
    path('contact/', contact, name='contact'),
    path('blog/category/<str:slug>', PostByCategory.as_view(), name='category'),
    path('blog/tag/<str:slug>', PostByTag.as_view(), name='tag'),
    path('post/<str:slug>', GetPost.as_view(), name='post'),
    path('test/', test, name='test'),
]
