from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.about_url = '/about/author/'
        cls.tech_url = '/about/tech/'
        cls.templates_url_names = {
            cls.about_url: 'about/author.html',
            cls.tech_url: 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        '''Страница с данными об авторе доступна любому пользователю.'''
        response = self.guest_client.get(AboutURLTests.about_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_exists_at_desired_location(self):
        '''Страница с данными о технологиях доступна любому пользователю.'''
        response = self.guest_client.get(AboutURLTests.tech_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in AboutURLTests.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
