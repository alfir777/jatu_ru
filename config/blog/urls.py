from django.contrib.sitemaps.views import sitemap
from django.urls import path

from rest_framework import routers

from .api import PostViewSet
from .feeds import LatestPostsFeed
from .sitemap import PostSitemap
from .views import (BlogByCategory, BlogByTag, BlogCreateView, BlogDeleteView, BlogDetailView, BlogListView,
                    BlogUpdateView, RobotsTxtView, Search, UserLogin, UserLogout, contact, get_profile, index,
                    register, restore_password)


sitemaps = {
    'posts': PostSitemap
}
router = routers.DefaultRouter()
router.register('api/posts', PostViewSet)

urlpatterns = [
    path('', index, name='home'),
    path('account/profile', get_profile, name='user_profile'),
    path('blog/blog_post_add', BlogCreateView.as_view(), name='blog_post_add'),
    path('blog/<str:slug>/edit', BlogUpdateView.as_view(), name='blog_post_edit'),
    path('blog/<str:slug>/delete', BlogDeleteView.as_view(), name='blog_post_delete'),
    path('blog/', BlogListView.as_view(), name='blog'),
    path('blog/<str:slug>', BlogDetailView.as_view(), name='post'),
    path('blog/category/<str:slug>', BlogByCategory.as_view(), name='category'),
    path('blog/tag/<str:slug>', BlogByTag.as_view(), name='tag'),
    path('contact/', contact, name='contact'),
    path('latest/feed/', LatestPostsFeed()),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('logout/', UserLogout.as_view(), name='user_logout'),
    path('register/', register, name='register'),
    path('restore_password/', restore_password, name='restore_password'),
    path('robots.txt', RobotsTxtView.as_view()),
    path('search/', Search.as_view(), name='search'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += router.urls
