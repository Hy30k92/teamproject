FROM docker.io/mariadb:10.6.19-focal

# 환경 변수 설정
ENV MYSQL_ROOT_PASSWORD=ubuntu
ENV MYSQL_DATABASE=ubuntu
ENV MYSQL_USER=ubuntu
ENV MYSQL_PASSWORD=ubuntu

# 초기화 SQL 스크립트 복사
COPY init-mysql.sql /docker-entrypoint-initdb.d/

# MariaDB 기본 포트 노출
EXPOSE 3306
