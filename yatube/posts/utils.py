from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet


def paginate_posts(
    request: WSGIRequest,
    posts_queryset: QuerySet
) -> Page:
    '''Возвращает объект страницы для страницы с постами и паджинатором.

    Параметры:
    request - объект http-запроса
    posts_queryset - набор постов из базы данных

    '''
    paginator = Paginator(posts_queryset, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
