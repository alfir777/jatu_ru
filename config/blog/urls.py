from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('portfolio/', portfolio, name='portfolio'),
    path('blog/', Blog.as_view(), name='blog'),
    path('contact/', contact, name='contact'),
    path('category/<str:slug>', get_category, name='category'),
    path('post/<str:slug>', get_post, name='post'),
    path('test/', test, name='test'),
]