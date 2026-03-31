from blog.repositories import (
    CategoryRepository,
    CommentRepository,
    PostRepository,
    TagRepository,
)
from blog.services import CommentService, ContactService, PostService, UserService

post_service = PostService(
    post_repo=PostRepository(),
    category_repo=CategoryRepository(),
    tag_repo=TagRepository(),
)

comment_service = CommentService(
    comment_repo=CommentRepository(),
)

contact_service = ContactService()

user_service = UserService()
