from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

UPLOAD_DIR = 'posts/'


class Group(models.Model):
    title = models.CharField(max_length=200, unique=True,
                             verbose_name='Название')
    slug = models.SlugField(unique=True,
                            verbose_name='Slug')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост')

    image = models.ImageField(
        'Картинка',
        upload_to=UPLOAD_DIR,
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments',
                             on_delete=models.CASCADE,
                             verbose_name='Пост')
    author = models.ForeignKey(User, related_name='comments',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created',)

    def __str__(self):
        return self.text[:20]


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE,
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, related_name='following',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
