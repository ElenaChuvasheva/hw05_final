import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

POSTS_GROUP = 11
POSTS_ANOTHER_GROUP = 2

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test_slug',
            description='Ещё одна тестовая группа',
        )

        cls.author = User.objects.create_user(username='test_author')
        cls.just_user = User.objects.create_user(username='just_user')
        cls.follower_user = User.objects.create_user(username='follower')
        cls.another_author = User.objects.create_user(
            username='another_author'
        )

        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.author
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        for post_number in range(1, POSTS_GROUP + 1):
            Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {post_number} группы',
                group=cls.group,
                image=cls.uploaded
            )

        for post_number in range(1, POSTS_ANOTHER_GROUP + 1):
            Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {post_number} другой группы',
                group=cls.another_group,
                image=cls.uploaded
            )

        cls.template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostsPagesTests.group.slug,)):
            'posts/group_list.html',
            reverse('posts:profile', args=(PostsPagesTests.author.username,)):
            'posts/profile.html',
            reverse('posts:post_detail', args=(1,)):
            'posts/post_detail.html',
            reverse('posts:post_edit', args=(1,)):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }

        cls.reverse_qsets = {
            reverse('posts:index'):
            Post.objects.all(),
            reverse(
                'posts:group_list',
                args=(PostsPagesTests.group.slug,)):
            PostsPagesTests.group.posts.select_related(),
            reverse(
                'posts:profile',
                args=(PostsPagesTests.author.username,)):
            PostsPagesTests.author.posts.select_related()
        }

        cls.form_fields_post = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.author)
        self.guest_client = Client()
        self.just_user_client = Client()
        self.just_user_client.force_login(PostsPagesTests.just_user)
        self.follower_user_client = Client()
        self.follower_user_client.force_login(PostsPagesTests.follower_user)

    def test_pages_use_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for reverse_name, template in (PostsPagesTests
                                       .template_pages_names.items()):
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        cache.clear()

    def test_paginator_page_show_correct_context(self):
        '''Шаблоны страниц с пагинатором имеют правильный контекст.'''
        for reverse_name, qset in PostsPagesTests.reverse_qsets.items():
            response = self.author_client.get(reverse_name)
            for object, post in zip(response.context.get('page_obj'),
                                    qset[:settings.POSTS_PER_PAGE]):
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(object, post)
        cache.clear()

    def test_first_paginator_page(self):
        '''Проверка: правильное количество постов на 1-й стр. пагинатора.'''
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(PostsPagesTests.group.slug,)),
            reverse('posts:profile', args=(PostsPagesTests.author.username,))
        )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
            self.assertEqual(
                len(response.context.get('page_obj')),
                settings.POSTS_PER_PAGE)
        cache.clear()

    def test_second_paginator_page(self):
        '''Проверка: правильное количество постов на 2-й стр. пагинатора.'''
        posts_sum = POSTS_GROUP + POSTS_ANOTHER_GROUP
        posts_index_page2 = posts_sum - settings.POSTS_PER_PAGE
        posts_group_page2 = POSTS_GROUP - settings.POSTS_PER_PAGE
        posts_profile_page2 = posts_sum - settings.POSTS_PER_PAGE

        reverse_posts = {
            reverse('posts:index'): posts_index_page2,
            reverse(
                'posts:group_list',
                args=(PostsPagesTests.group.slug,)):
            posts_group_page2,
            reverse(
                'posts:profile',
                args=(PostsPagesTests.author.username,)):
            posts_profile_page2
        }

        for reverse_name, number_of_posts in reverse_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj')), number_of_posts)
        cache.clear()

    def test_post_page_show_correct_context(self):
        '''Шаблон страницы поста имеет правильный контекст.'''
        post = Post.objects.get(pk=1)
        response = self.author_client.get(
            reverse('posts:post_detail', args=(post.pk,)))
        post_from_page = response.context.get('post')

        self.assertEqual(post_from_page, post)
        cache.clear()

    def test_post_create_page_show_correct_context(self):
        '''Форма создания поста имеет правильные поля.'''
        response = self.author_client.get(reverse('posts:post_create'))

        for value, expected in PostsPagesTests.form_fields_post.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_form(self):
        '''Форма создания поста имеет правильные поля.'''
        response = self.author_client.get(reverse('posts:post_create'))

        for value, expected in PostsPagesTests.form_fields_post.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        '''Форма редактирования поста имеет правильные поля.'''
        post = Post.objects.get(pk=1)

        response = self.author_client.get(
            reverse('posts:post_edit', args=(post.pk,)))

        for value, expected in PostsPagesTests.form_fields_post.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_form_value(self):
        '''Содержимое поста передаётся на страницу редактирования.'''
        post = Post.objects.get(pk=1)

        response = self.author_client.get(
            reverse('posts:post_edit', args=(post.pk,)))
        post_from_page = response.context['form'].instance

        self.assertEqual(post_from_page, post)
        self.assertTrue(response.context['is_edit'])

    def test_new_post_on_its_pages(self):
        '''Новый пост в группе попадает на нужные страницы.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Новый пост группы',
            group=PostsPagesTests.group
        )
        reverse_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', args=(PostsPagesTests.group.slug,)),
            reverse('posts:profile', args=(PostsPagesTests.author.username,))
        )

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                last_post = response.context.get('page_obj')[0]
                self.assertEqual(last_post, new_post)

        cache.clear()

    def test_new_post_not_in_another_group(self):
        '''Новый пост в группе не попадает на страницу другой группы.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Новый пост группы',
            group=PostsPagesTests.group
        )

        response = self.author_client.get(reverse(
            'posts:group_list', args=(PostsPagesTests.another_group.slug,)))

        for post in response.context.get('page_obj'):
            self.assertNotEqual(post, new_post)

        cache.clear()

    def test_image_to_paginated_pages(self):
        '''Картинка попадает на страницу главную, группы, профиля.'''
        for reverse_name, qset in PostsPagesTests.reverse_qsets.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                page = response.context.get('page_obj')
                last_post_page = page[0]
                last_post_db = qset[0]
                self.assertEqual(last_post_page.image, last_post_db.image)

        cache.clear()

    def test_image_to_post_page(self):
        '''Картинка попадает на страницу поста'''
        post_with_image = Post.objects.get(pk=1)

        response = self.author_client.get(
            reverse('posts:post_detail', args=(post_with_image.pk,))
        )
        post_from_page = response.context.get('post')

        self.assertIsNotNone(post_from_page.image)
        self.assertEqual(post_with_image.image, post_from_page.image)

    def test_comment_authorized(self):
        '''Комментировать посты может только авторизованный пользователь.'''
        redirect_to = (reverse('users:login')
                       + '?next=' + reverse('posts:add_comment', args=(1,)))

        response = self.guest_client.post(
            reverse('posts:add_comment', args=(1,)),
            data={'text': 'Текст комментария'},
        )

        self.assertRedirects(response, redirect_to)

    def test_comment_to_post_page(self):
        '''Комментарий появляется на странице поста'''
        post = Post.objects.get(pk=1)
        new_comment = Comment.objects.create(
            post=post,
            author=PostsPagesTests.author,
            text='Текст комментария'
        )

        response = self.author_client.get(reverse(
            'posts:post_detail', args=(post.pk,)))
        comments_from_page = response.context.get('comments')

        self.assertEqual(new_comment, comments_from_page[0])

    def test_cache_add(self):
        '''Пост кэшируется на главной странице.'''
        Post.objects.create(
            author=PostsPagesTests.author,
            text='Пост для тестирования кэша',
            group=PostsPagesTests.group
        )

        cache_after_add = self.author_client.get(
            reverse('posts:index')
        ).content

        self.assertIn('Пост для тестирования кэша'.encode(), cache_after_add)
        cache.clear()

    def test_cache_delete(self):
        '''Пост остаётся в кэше после удаления.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Пост для кэша',
            group=PostsPagesTests.group
        )

        cache_before_delete = self.author_client.get(
            reverse('posts:index')
        ).content

        self.assertIn('Пост для кэша'.encode(), cache_before_delete)

        new_post.delete()

        cache_after_delete = self.author_client.get(
            reverse('posts:index')
        ).content

        self.assertIn('Пост для кэша'.encode(), cache_after_delete)

        cache.clear()

        cache_after_clear = self.author_client.get(
            reverse('posts:index')
        ).content

        self.assertNotIn('Пост для кэша'.encode(), cache_after_clear)

        cache.clear()

    def test_follow(self):
        '''Можно подписаться на автора.'''
        number_follows_start = PostsPagesTests.follower_user.follower.count()

        self.follower_user_client.get(
            reverse('posts:profile_follow',
                    args=(PostsPagesTests.another_author.username,))
        )

        number_follows_create = PostsPagesTests.follower_user.follower.count()
        difference = number_follows_create - number_follows_start

        self.assertEqual(difference, 1)

    def test_unfollow(self):
        '''Можно отписаться от автора.'''
        Follow.objects.create(
            user=PostsPagesTests.follower_user,
            author=PostsPagesTests.another_author
        )
        number_follows_start = PostsPagesTests.follower_user.follower.count()

        self.follower_user_client.get(
            reverse('posts:profile_unfollow',
                    args=(PostsPagesTests.another_author.username,))
        )

        number_follows_delete = PostsPagesTests.follower_user.follower.count()
        difference = number_follows_start - number_follows_delete

        self.assertEqual(difference, 1)

    def test_follow_page(self):
        '''Новая запись появляется только в ленте подписчиков.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Новый пост в ленте',
            group=PostsPagesTests.group
        )

        follower_response = self.follower_user_client.get(
            reverse('posts:follow_index')
        )
        last_post = follower_response.context.get('page_obj')[0]

        self.assertEqual(last_post, new_post)

        just_user_response = self.just_user_client.get(
            reverse('posts:follow_index')
        )

        for post in just_user_response.context.get('page_obj'):
            self.assertNotEqual(post, new_post)
