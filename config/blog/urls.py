from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('portfolio/', portfolio, name='portfolio'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),
    path('category/<str:slug>', get_category, name='category'),
    path('test/', test, name='test'),
]