from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Category, Post

USER_EMAIL = 'test@company.com'
OLD_PASSWORD = 'TestPassword1#'
NUMBER_OF_ITEMS = 10


class BlogTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('user', password='password')
        test_user.save()
        test_category = Category.objects.create(title='Test', slug='Test')

        for item_index in range(NUMBER_OF_ITEMS):
            Post.objects.create(
                title=f'title {item_index}',
                slug=f'{item_index}',
                description=f'description {item_index}',
                author_id=test_user.id,
                category_id=test_category.id,
            )

    def test_blog_url_exists_at_desired_location(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_blog_uses_correct_template(self):
        response = self.client.get(reverse('blog'))
        self.assertTemplateUsed(response, 'blog/blog.html')

    def test_post_list_view(self):
        response = self.client.get(reverse('blog'))
        self.assertContains(response, 'title 1')


class PostByCategoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('user', password='password')
        test_user.save()
        test_category = Category.objects.create(title='test_category', slug='test_category')

        for item_index in range(NUMBER_OF_ITEMS):
            Post.objects.create(
                title=f'title {item_index}',
                slug=f'{item_index}',
                description=f'description {item_index}',
                author_id=test_user.id,
                category_id=test_category.id,
            )

    def test_post_by_category_url_exists_at_desired_location(self):
        response = self.client.get('/blog/category/test_category')
        self.assertEqual(response.status_code, 200)

    def test_post_by_category_uses_correct_template(self):
        response = self.client.get('/blog/category/test_category')
        self.assertTemplateUsed(response, 'blog/category.html')

    def test_post_by_category_list_view(self):
        response = self.client.get('/blog/category/test_category')
        self.assertContains(response, 'title 1')


class ContactTest(TestCase):

    def test_contact_url_exists_at_desired_location(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)

    def test_contact_uses_correct_template(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/contact.html')


class IndexTest(TestCase):

    def test_index_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/index.html')


class RestorePasswordTest(TestCase):

    def test_restore_password_url_exists_at_desired_location(self):
        response = self.client.get('/restore_password/')
        self.assertEqual(response.status_code, 200)

    def test_restore_password_uses_correct_template(self):
        response = self.client.get(reverse('restore_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/restore_password.html')

    def test_post_restore_password(self):
        _ = User.objects.create(username='test', email=USER_EMAIL)
        response = self.client.post(reverse('restore_password'), {'email': USER_EMAIL})
        self.assertEqual(response.status_code, 200)
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertIn(USER_EMAIL, outbox[0].to)

    def test_if_password_was_changed(self):
        user = User.objects.create(username='test', email=USER_EMAIL)
        user.set_password(OLD_PASSWORD)
        user.save()
        old_password_hash = user.password
        response = self.client.post(reverse('restore_password'), {'email': USER_EMAIL})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertNotEqual(old_password_hash, user.password)


class RobotsTxtTests(TestCase):
    def test_get(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        self.assertTemplateUsed(response, 'robots.txt')
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")

        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)
