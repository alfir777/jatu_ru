from http import HTTPStatus
from xml.dom.minidom import parseString

from django.contrib.auth.models import User
from django.test import TestCase

from blog.models import Category, Post

NUMBER_OF_ITEMS = 50


class PostSitemapTests(TestCase):
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

    def test_get(self):
        response = self.client.get("/sitemap.xml")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "application/xml")

        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], '<?xml version="1.0" encoding="UTF-8"?>')
        self.assertEqual(lines[1], '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                   'xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    def test_post_ok(self):
        response = self.client.post("/sitemap.xml")

        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_items(self):
        response = self.client.get("/sitemap.xml")
        parsed_xml = parseString(response.content)
        url_tags = parsed_xml.getElementsByTagName("url")
        self.assertEqual(len(url_tags), NUMBER_OF_ITEMS)

    def test_lastmod(self):
        response = self.client.get("/sitemap.xml")
        parsed_xml = parseString(response.content)
        lastmod_tags = parsed_xml.getElementsByTagName("lastmod")
        self.assertEqual(len(lastmod_tags), NUMBER_OF_ITEMS)
