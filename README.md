#  Foodgram
![workflow status](https://github.com/PROaction/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание

Проект Foodgram это место для размещения рецептов.

## Стек
### Backend
- Python
- Django
- PostgresQL
### Frontend
- JS
- React
### Серверная часть
- Nginx
- Gunicorn

## Инструкция по развертыванию
1. Настроить Nginx на сервере, например:
```
server {
        server_name proactionkittygram.ddns.net;
        location / {
                proxy_pass http://127.0.0.1:9090;
        }



    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/proactionkittygram.ddns.net/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/proactionkittygram.ddns.net/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
```
2. Создать .env-файл и скопировать его в директорию проекта на сервере
```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=5432
SECRET_KEY=<Django secret key>
DEBUG=<True or False>
ALLOWED_HOSTS=51.250.23.70, proactionkittygram.ddns.net
USE_SQLITE=<True or empty>
```
3. Скопировать файл docker-compose.production.yml в директорию проекта на сервере
4. Перейти в директорию с файлом и выполнить команду
```
sudo docker compose -f docker-compose.production.yml up -d
```

Автор: Сергей Попов