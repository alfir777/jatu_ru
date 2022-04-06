# Блог JaTu.Ru

<img src="https://github.com/alfir777/jatu_ru/workflows/CI/badge.svg?branch=master">

Блог на Django 3, реализован без привязки к домену

## Запуск
1. Клонировать репозиторий или форк
```
git clone https://github.com/alfir777/jatu_ru.git
```
2. Выполнить копирование файла .env_template на .env и выставить свои параметры
```
cd jatu_ru/
cp .env_template .env
```
3. В Dockerfile заменить app на Вашего пользователя и его UID/GID
4. Создать acme.json для traefik и дать права
```
touch acme.json
chmod 600 acme.json
```
5. Развернуть контейнеры с помощью в docker-compose
```
docker-compose -f docker-compose.yml up -d
```
6. Выполнить миграции/сбор статики
```
 docker exec -it web python3 manage.py makemigrations
 docker exec -it web python3 manage.py migrate
 docker exec -it web python3 manage.py collectstatic
```
7. Создать суперпользователя
```
 docker exec -it web python3 manage.py createsuperuser
```
Возможны проблемы с правами на папки, созданными docker/django
- Изменить права доступа для директорий на 755 (drwxr-xr-x)
```
find /path/to/target/dir -type d -exec chmod 755 {} \;
```
- Изменить права доступа для файлов на 644 (-rw-r--r--)
```
find /path/to/target/dir -type f -exec chmod 644 {} \;
```
- Не всегда выполняются все миграции, принудительно:
```
 docker exec -it web python3 manage.py migrate --run-syncdb
```