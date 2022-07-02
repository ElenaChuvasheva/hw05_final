from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Очень длинный больше 15 знаков текст поста',
        )

    def test_groups_have_correct_object_names(self):
        '''Проверяем, что у модели Group корректно работает __str__.'''
        self.assertEqual(
            str(PostModelTest.group), PostModelTest.group.title,
            'Имя объекта группы не совпадает с названием группы')

    def test_posts_have_correct_object_names(self):
        '''Проверяем, что у модели Post корректно работает __str__.'''
        self.assertEqual(
            str(PostModelTest.post), PostModelTest.post.text[:15],
            'Имя объекта поста не совпадает с первыми 15 символами поста')

    def test_verbose_name(self):
        '''Проверяем корректность verbose_name.'''
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected)

    def test_help_text(self):
        '''Проверяем корректность help_text.'''
        field_helps = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, expected in field_helps.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected)
