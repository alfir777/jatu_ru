from blog.views.blog import (
    BlogByCategory,
    BlogByTag,
    BlogCreateView,
    BlogDeleteView,
    BlogDetailView,
    BlogListView,
    BlogUpdateView,
)
from blog.views.contact import contact
from blog.views.index import RobotsTxtView, index
from blog.views.search import Search
from blog.views.user import (
    UserLogin,
    UserLogout,
    get_profile,
    register,
    restore_password,
)

__all__ = [
    "BlogListView",
    "BlogDetailView",
    "BlogCreateView",
    "BlogUpdateView",
    "BlogDeleteView",
    "BlogByCategory",
    "BlogByTag",
    "UserLogin",
    "UserLogout",
    "Search",
    "RobotsTxtView",
    "index",
    "contact",
    "get_profile",
    "register",
    "restore_password",
]
