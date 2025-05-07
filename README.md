# Домашняя работа к модулю 9

# Тема 35.2 CI/CD и GitHub Actions

# 1. Ручной деплой приложения на удалённом сервере YC

## 1. Для запуска приложения на удалённом сервере использован докер-конетейнер.

Сервисы:

* **web** - сервис приложения;

* **db** - серваис БД, в качестве БД используется PostgreSQL;

* **redis** - «очередь заданий», которые должен выполнить Celery;

* **celery** - сервис для отложенных задач;

* **celery-beat** - сервис для периодических задач;

* **nginx** - это фронтенд веб-сервер (reverse proxy);


## 2. Ручной деплой сервера в облаке

Целью работы является деплой контейнера с приложением Django.

Для размещения докер-контейнера создано облако в Яндекс-cloud

HostName ```5.35.108.203```

Используется Ubuntu 22.04.

Открыты порты:
- 22 - SSH);
- 80 - HTTP);
- 443 - HTTPS;
- 8000 - порт приложения

Запуск приложения происходит через Gunicorn. Связка такая:

```scss
[Браузер] → HTTP → [Nginx] → WSGI (через proxy_pass) → [Gunicorn] → [Django] → [Ответ] → [Nginx] → [Браузер]
```

Как работает связка:
1. Nginx принимает HTTP-запрос от клиента.
2. Nginx пересылает этот запрос Gunicorn.
3. Gunicorn запускает Django-приложение по WSGI-протоколу.
4. Django обрабатывает запрос и возвращает ответ через Gunicorn обратно в Nginx.
5. Nginx отправляет ответ клиенту.

Gunicorn:
- запускает само Django-приложение;
- принимает HTTP-запросы и передаёт их Django через WSGI-интерфейс;
- обрабатывает Python-код (вызовы view-функций, работу ORM, шаблоны и т.д.);
- отвечает только за backend-логику.

Nginx:
- принимает все входящие запросы от клиента (например, браузера);
- перенаправляет (proxy_pass) запросы на Gunicorn, если это Django-прослойка (/api, /admin, и т.п.);
- отдаёт напрямую статические файлы (/static/, /media/);

## 3. Автозапуск сервера

Для автозапуска используется Systemd.
Почему именно Systemd?
- Уже установлен в большинстве систем.
- Не требует дополнительной установки.
- Используется для запуска почти всех служб (nginx, postgres, ssh и т.д.).

В YC проект находится по пути: ```/home/stasm226/homework-35-2```

Для запуска создан unit-файл для Systemd
```/etc/systemd/system/school.service:```

```ini
# /etc/systemd/system/school.service
[Unit]
Description=School Django Project (Docker Compose)
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/stasm226/homework-35-2
ExecStart=/usr/bin/docker compose up -d --build
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Команды для запуска:

1. Перезагружаем systemd
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
```

2. Включаем автозапуск
```bash
sudo systemctl enable school.service
```

3. Запускаем проект
```bash
 sudo systemctl start school.service
 ```

4. Проверяем статус
```bash
sudo systemctl status school.service
```

5. Результат запуска
```
● school.service - School Django Project (Docker Compose)
     Loaded: loaded (/etc/systemd/system/school.service; enabled; preset: enabled)
     Active: active (exited) since Tue 2025-05-06 14:35:12 UTC; 19s ago
    Process: 528585 ExecStart=/usr/bin/docker compose up -d --build (code=exited, status=0/SUCCESS)
   Main PID: 528585 (code=exited, status=0/SUCCESS)
        CPU: 293ms

May 06 14:35:10 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container homework-35-2-redis-1  Started
May 06 14:35:10 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container celery-beat  Starting
May 06 14:35:10 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container school  Starting
May 06 14:35:10 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container celery  Starting
May 06 14:35:11 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container celery-beat  Started
May 06 14:35:11 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container celery  Started
May 06 14:35:11 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container school  Started
May 06 14:35:11 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container nginx  Starting
May 06 14:35:12 compute-vm-2-2-20-ssd-1746184035719 docker[528600]:  Container nginx  Started
May 06 14:35:12 compute-vm-2-2-20-ssd-1746184035719 systemd[1]: Finished school.service - School Django Project (Docker Compose).
```

# 2. CI/CD

Для осуществления CI/CD настроены Github Actions.
В Github Secrets сохранены необходивые переменные:
DJANGO_ALLOWED_HOSTS, DJANGO_SECRET_KEY, DOCKER_PASSWORD, DOCKER_USERNAME, SERVER_IP, SSH_PRIVATE_KEY, SSH_USER.

CI-pipline настроен для событий push и pull_request для ветки main.

Jobs:
- lint - flake8
- test - 30 тестов
- build
- deploy
