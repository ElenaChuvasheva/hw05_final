import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import UPLOAD_DIR, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test_slug',
            description='Тестовое описание другой группы',
        )
        cls.author = User.objects.create_user(username='JustUser')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост группы',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)

    def test_create_post(self):
        '''Валидная форма создаёт запись в Post.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': PostFormTests.group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=(PostFormTests.author.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст нового поста',
                author=PostFormTests.author,
                group=PostFormTests.group
            ).exists()
        )

    def test_create_post_with_image(self):
        '''Валидная форма создаёт запись с картинкой в Post'''
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Текст поста с картинкой',
            'group': PostFormTests.group.pk,
            'image': uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=(PostFormTests.author.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста с картинкой',
                author=PostFormTests.author,
                group=PostFormTests.group,
            ).exists()
        )
        newpost = Post.objects.get(text='Текст поста с картинкой')
        filename = UPLOAD_DIR + uploaded.name
        self.assertIn(filename, newpost.image.name)

    def test_edit_post(self):
        '''Валидная форма изменяет запись в Post.'''
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Обновлённый текст поста',
            'group': PostFormTests.another_group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(PostFormTests.post.pk,)),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(PostFormTests.post.pk,)))
        self.assertTrue(
            Post.objects.filter(
                text='Обновлённый текст поста',
                author=PostFormTests.author,
                group=PostFormTests.another_group
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)
