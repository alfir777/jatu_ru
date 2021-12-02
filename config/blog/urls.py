from django.urls import path
from django.contrib.sitemaps.views import sitemap
from rest_framework import routers

from .api import PostViewSet
from .views import *
from .sitemap import PostSitemap
from .feeds import LatestPostsFeed

sitemaps = {
    'posts': PostSitemap
}
router = routers.DefaultRouter()
router.register('api/posts', PostViewSet)

urlpatterns = [
    path('', index, name='home'),
    path('blog/', Blog.as_view(), name='blog'),
    path('blog/blog_add_post>', blog_add_post, name='blog_add_post'),
    path('contact/', contact, name='contact'),
    path('latest/feed/', LatestPostsFeed()),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('logout/', UserLogout.as_view(), name='user_logout'),
    path('register/', register, name='register'),
    path('restore_password/', restore_password, name='restore_password'),
    path('robots.txt', RobotsTxtView.as_view()),
    path('search/', Search.as_view(), name='search'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('blog/category/<str:slug>', PostByCategory.as_view(), name='category'),
    path('blog/tag/<str:slug>', PostByTag.as_view(), name='tag'),
    path('post/<str:slug>', GetPost.as_view(), name='post'),
    path('account/profile', get_profile, name='user_profile'),
]

urlpatterns += router.urls
