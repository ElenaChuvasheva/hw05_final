from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='test_author')
        cls.just_user = User.objects.create_user(username='just_user')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.index_url = '/'
        cls.group_url = f'/group/{cls.group.slug}/'
        cls.profile_url = f'/profile/{cls.author.username}/'
        cls.post_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.create_url = '/create/'
        cls.follow_index_url = '/follow/'
        cls.public_urls = {
            cls.index_url: 'posts/index.html',
            cls.group_url: 'posts/group_list.html',
            cls.profile_url: 'posts/profile.html',
            cls.post_url: 'posts/post_detail.html',
        }
        cls.private_urls = {
            cls.create_url: 'posts/create_post.html',
            cls.post_edit_url: 'posts/create_post.html',
            cls.follow_index_url: 'posts/follow.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.just_user)
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.author)

    def test_index_url_exists_at_desired_location_anonymous(self):
        '''Главная страница доступна любому пользователю.'''
        response = self.guest_client.get(PostsURLTests.index_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        cache.clear()

    def test_group_url_exists_at_desired_location_anonymous(self):
        '''Страница группы доступна любому пользователю.'''
        response = self.guest_client.get(PostsURLTests.group_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location_anonymous(self):
        '''Страница профиля доступна любому пользователю.'''
        cache.clear()
        response = self.guest_client.get(PostsURLTests.profile_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists_at_desired_location_anonymous(self):
        '''Страница поста доступна любому пользователю.'''
        response = self.guest_client.get(PostsURLTests.post_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        '''Запрос к несуществующей странице вернёт ошибку 404.'''
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location(self):
        '''Страница создания поста доступна авторизованному пользователю.'''
        response = self.authorized_client.get(PostsURLTests.create_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_redirect_anonymous(self):
        '''Страница создания поста перенаправляет анонимного пользователя.'''
        response = self.guest_client.get(PostsURLTests.create_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_redirect_anonymous(self):
        '''Страница редактирования перенаправляет анонимного пользователя.'''
        response = self.guest_client.get(PostsURLTests.post_edit_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница редактирования доступна автору.'''
        response = self.author_client.get(PostsURLTests.post_edit_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_non_author_on_login(self):
        '''Страница редактирования перенаправит не-автора.'''
        response = self.authorized_client.get(PostsURLTests.post_edit_url)

        self.assertRedirects(response, PostsURLTests.post_url)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for address, template in {
            **PostsURLTests.private_urls,
            **PostsURLTests.public_urls
        }.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

        cache.clear()
