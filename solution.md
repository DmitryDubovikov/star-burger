# step 1

На windows 11 у меня не работает ssh forwarding. Вероятно, из-за разных версий. Поэтому если предполагается работа с git, то нужно из Ubuntu подключатся. В selectel добавлены SSH-ключи пользователя root и для Windows и для Ubuntu.

```
ssh-add (в Ubuntu)
ssh myselectel
```


# step 3

windows 11: C:\Users\dima\.ssh 
```
Host myselectel
    HostName 77.105.168.57
    User root
    ForwardAgent yes
```
ubuntu: /etc/ssh/sshd_config
```
проверить, что у меня в убунту
...
```

# step 4

SSH Agent Forwarding на сервере:  GitHub не требует логина и пароля.
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding
```
root@formidable-cusna:/etc/ssh# cat sshd_config
AllowAgentForwarding yes
```

# step 7
Демонизация. В каталоге /etc/systemd/system
```
root@formidable-cusna:/etc/systemd/system# cat star-burger.service
# Configuration is dased on official Gunicorn docs: https://docs.gunicorn.org/en/latest/deploy.html?highlight=systemd#systemd
[Unit]
Description=Django micro-service to serve star_burger project
Requires=dockerpostgres.service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/star-burger/
ExecStart=/opt/star-burger/venv/bin/gunicorn -b 127.0.0.1:8080 --workers 3 star_burger.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
```

# step 8

```
root@formidable-cusna:/opt/star-burger/star_burger# cat .env
SECRET_KEY="***"
YANDEX_GEOCODER_API_KEY=***
ROLLBAR_TOKEN=***
DB_URL='postgresql://***:***@localhost:5432/star_burger_db'
```

# step 10 Nginx
Установка по туториалу
https://www.digitalocean.com/community/tutorials/nginx-ubuntu-18-04-ru
```
root@formidable-cusna:/etc/systemd/system# systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2023-06-13 15:20:55 UTC; 1 week 3 days ago

```



# step ? Docker Container for Postgres
```
root@formidable-cusna:/etc/systemd/system# cat dockerpostgres.service
[Unit]
Description=My Docker Container for Postgres
After=docker.service
Requires=docker.service

[Service]
ExecStart=/usr/bin/docker run --rm -p 5432:5432 -v my-postgres-data:/var/lib/postgresql/data --name my-postgres my-postgres
ExecStop=/usr/bin/docker stop my-postgres

[Install]
WantedBy=default.target
```

