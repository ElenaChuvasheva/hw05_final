# Описание
Социальная сеть Yatube для публикации дневников. Используются формы, пагинация страниц, кеширование главной страницы. Проект запущен в Яндекс.Облаке.

# Технологии
Python 3, Django, html, cache, sorl-thumbnail, SQLite

# Запуск в dev режиме
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone <адрес репозитория>
```
```
cd hw05_final/
```

Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
