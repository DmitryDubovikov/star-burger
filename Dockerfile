FROM postgres

# Настраиваем переменные среды
ENV POSTGRES_USER postgres_user    
ENV POSTGRES_PASSWORD postgres_password
ENV POSTGRES_DB star_burger_db

# Создаем директорию для примонтированного тома
RUN mkdir -p /var/lib/postgresql/data

# Устанавливаем права доступа для директории
RUN chown -R postgres:postgres /var/lib/postgresql/data

# Указываем точку монтирования для примонтированного тома
VOLUME /var/lib/postgresql/data

# Открываем порт для подключений к PostgreSQL
EXPOSE 5432
