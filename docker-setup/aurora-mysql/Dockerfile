FROM mysql:5.7.17

# Copy migration files to the MySQL initialization folder
ADD ./migrations /docker-entrypoint-initdb.d/

CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]