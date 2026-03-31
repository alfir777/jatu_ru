class BlogException(Exception):
    pass


class PostNotFoundError(BlogException):
    pass


class CategoryNotFoundError(BlogException):
    pass


class TagNotFoundError(BlogException):
    pass


class DuplicatePostTitleError(BlogException):
    pass


class UnauthorizedError(BlogException):
    pass


class EmailSendError(BlogException):
    pass
