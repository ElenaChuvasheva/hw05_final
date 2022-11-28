# Социальная сеть Yatube

## Описание
Социальная сеть для публикации дневников. Используются формы, пагинация страниц, кеширование главной страницы.

Залогиненные пользователи могут создавать посты с текстом и картинками. Есть группы по темам постов. Реализованы подписки на авторов.

## Технологии
Python 3, Django, cache, sorl-thumbnail, SQLite, HTML

## Запуск в dev режиме
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone <адрес репозитория>
```
```
cd hw05_final/
```
Cоздайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/bin/activate
```
Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Перейдите в папку yatube с файлом manage.py:
```
cd .\yatube\
```
Зайдите в shell:
```
python manage.py shell
```
и выполните там команду для получения SECRET_KEY:
```
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Запишите SECRET_KEY в соответствующее место в файле settings.py.
Выполните миграции:
```
python manage.py migrate
```
Запустите проект:
```
python manage.py runserver
```
