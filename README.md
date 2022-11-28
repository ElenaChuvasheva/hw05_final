# Социальная сеть Yatube

## Описание
Социальная сеть для публикации дневников. Используются формы, пагинация страниц, кеширование главной страницы.

Залогиненные пользователи могут создавать посты с текстом и картинками. Есть группы по темам постов. Реализованы подписки на авторов.

## Технологии
Python 3, Django, HTML, cache, sorl-thumbnail, SQLite

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
Выполните миграции:
```
python manage.py migrate
```
Запустите проект:
```
python manage.py runserver
```
