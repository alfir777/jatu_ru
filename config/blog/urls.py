from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('blog/', Blog.as_view(), name='blog'),
    path('contact/', contact, name='contact'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('portfolio/', portfolio, name='portfolio'),
    path('register/', register, name='register'),
    path('search/', Search.as_view(), name='search'),
    path('test/', test, name='test'),
    path('blog/category/<str:slug>', PostByCategory.as_view(), name='category'),
    path('blog/tag/<str:slug>', PostByTag.as_view(), name='tag'),
    path('post/<str:slug>', GetPost.as_view(), name='post'),
]
